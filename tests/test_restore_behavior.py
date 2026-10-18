import os
import shutil
import tempfile
import unittest
from unittest import mock

import dev_cleaner


class AppMoverRestoreTests(unittest.TestCase):
    def run_restore(self, directory, copy_code=1, corrupt=False, save_error=False, timed_out=False,
                    retry_history=False, target_symlink=False):
        target = os.path.join(directory, "target")
        orig = os.path.join(directory, "original")
        os.mkdir(target)
        with open(os.path.join(target, "app.bin"), "wb") as file:
            file.write(b"original data")
        record = {"name": "Example", "original_path": orig, "target_path": target, "size_bytes": 13}
        app = dev_cleaner.DevAICleanerApp.__new__(dev_cleaner.DevAICleanerApp)
        app.log = mock.Mock()
        app.after = mock.Mock()
        app.app_items = []
        app.refresh_restore_list = mock.Mock()
        app._render_app_row = mock.Mock()

        def copy(command, **kwargs):
            self.assertEqual(kwargs["creationflags"], dev_cleaner.hidden_console_creation_flags())
            self.assertGreater(kwargs.get("timeout", 0), 0)
            if timed_out:
                raise dev_cleaner.subprocess.TimeoutExpired(command, kwargs["timeout"])
            shutil.copytree(command[1], command[2], dirs_exist_ok=True)
            if corrupt:
                with open(os.path.join(command[2], "app.bin"), "wb") as file:
                    file.write(b"corrupt data!")
            return mock.Mock(returncode=copy_code)

        islink = os.path.islink
        with mock.patch.object(dev_cleaner.os.path, "islink",
                               side_effect=lambda path: (target_symlink and path == target) or islink(path)), \
                mock.patch.object(dev_cleaner, "stop_processes_in_folder"), \
                mock.patch.object(dev_cleaner.subprocess, "run", side_effect=copy), \
                mock.patch.object(dev_cleaner, "load_moves_history", return_value=[record]), \
                mock.patch.object(dev_cleaner, "save_moves_history",
                                  side_effect=[OSError("history locked"), None, None] if retry_history else
                                  OSError("history locked") if save_error else None) as save:
            app._bg_restore_app(record)
            if retry_history:
                self.assertFalse(os.path.lexists(orig))
                app._bg_restore_app(record)
        return app, record, save

    def test_symlink_target_is_rejected_without_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            app, record, save = self.run_restore(directory, target_symlink=True)
            self.assertTrue(os.path.isfile(os.path.join(record["target_path"], "app.bin")))
            self.assertFalse(os.path.lexists(record["original_path"]))
            save.assert_not_called()
            app.after.assert_not_called()

    def test_timed_out_copy_preserves_target_and_history(self):
        with tempfile.TemporaryDirectory() as directory:
            app, record, save = self.run_restore(directory, timed_out=True)
            self.assertTrue(os.path.isfile(os.path.join(record["target_path"], "app.bin")))
            self.assertFalse(os.path.lexists(record["original_path"]))
            save.assert_not_called()
            app.after.assert_not_called()

    def test_failed_copy_keeps_restore_record_and_source(self):
        with tempfile.TemporaryDirectory() as directory:
            app, record, save = self.run_restore(directory, copy_code=8)
            self.assertTrue(os.path.isdir(record["target_path"]))
            self.assertFalse(os.path.lexists(record["original_path"]))
            save.assert_not_called()
            app.after.assert_not_called()

    def test_copy_exit_success_with_changed_content_is_not_success(self):
        with tempfile.TemporaryDirectory() as directory:
            app, record, save = self.run_restore(directory, corrupt=True)
            self.assertTrue(os.path.isdir(record["target_path"]))
            self.assertFalse(os.path.lexists(record["original_path"]))
            save.assert_not_called()
            app.after.assert_not_called()

    def test_history_failure_preserves_target_and_reports_problem(self):
        with tempfile.TemporaryDirectory() as directory:
            app, record, save = self.run_restore(directory, save_error=True)
            self.assertTrue(os.path.isdir(record["target_path"]))
            self.assertTrue(any("history locked" in call.args[0] for call in app.log.call_args_list))
            app.after.assert_not_called()

    def test_history_failure_rolls_back_owned_original_for_safe_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            app, record, save = self.run_restore(directory, retry_history=True)
            self.assertFalse(os.path.exists(record["target_path"]))
            self.assertTrue(os.path.isfile(os.path.join(record["original_path"], "app.bin")))
            self.assertEqual(save.call_count, 3)
            self.assertEqual(app.after.call_count, 1)

    def test_history_write_failure_propagates_and_preserves_previous_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "moves.json")
            with open(path, "w", encoding="utf-8") as file:
                file.write("[]")
            with mock.patch.object(dev_cleaner, "MOVES_HISTORY_DIR", directory), \
                    mock.patch.object(dev_cleaner, "MOVES_HISTORY_FILE", path), \
                    mock.patch.object(dev_cleaner.os, "replace", side_effect=OSError("locked")):
                with self.assertRaises(OSError):
                    dev_cleaner.save_moves_history([{"name": "Example"}])
            with open(path, encoding="utf-8") as file:
                self.assertEqual(file.read(), "[]")

    def test_target_cleanup_failure_records_pending_cleanup_state(self):
        with tempfile.TemporaryDirectory() as directory:
            target = os.path.join(directory, "target")
            orig = os.path.join(directory, "original")
            os.mkdir(target)
            with open(os.path.join(target, "app.bin"), "wb") as file:
                file.write(b"original data")
            record = {"name": "Example", "original_path": orig, "target_path": target, "size_bytes": 13}
            app = dev_cleaner.DevAICleanerApp.__new__(dev_cleaner.DevAICleanerApp)
            app.log = mock.Mock()
            app.after = mock.Mock()
            app.app_items = []
            app.refresh_restore_list = mock.Mock()
            app._render_app_row = mock.Mock()

            def copy(command, **kwargs):
                shutil.copytree(command[1], command[2], dirs_exist_ok=True)
                return mock.Mock(returncode=1)

            saved = []
            with mock.patch.object(dev_cleaner, "stop_processes_in_folder"), \
                    mock.patch.object(dev_cleaner.subprocess, "run", side_effect=copy), \
                    mock.patch.object(dev_cleaner, "load_moves_history", return_value=[record]), \
                    mock.patch.object(dev_cleaner, "save_moves_history", side_effect=lambda recs: saved.append(list(recs))), \
                    mock.patch.object(dev_cleaner, "cleanup_verified_copy", side_effect=OSError("locked target")):
                app._bg_restore_app(record)

            self.assertTrue(os.path.isfile(os.path.join(orig, "app.bin")))
            self.assertTrue(os.path.isfile(os.path.join(target, "app.bin")))
            self.assertEqual(saved[-1][0]["phase"], "restored_pending_cleanup")
            self.assertIn("manifest", saved[-1][0])
            app.after.assert_called_once_with(0, app.refresh_restore_list)

    def test_pending_cleanup_row_shows_retry_action(self):
        app = dev_cleaner.DevAICleanerApp.__new__(dev_cleaner.DevAICleanerApp)
        app.restore_scroll = mock.Mock()
        app.restore_scroll.winfo_children.return_value = []
        record = {"name": "Example", "original_path": "C:/Example", "target_path": "D:/Example",
                  "phase": "restored_pending_cleanup", "manifest": {}}
        with mock.patch.object(dev_cleaner, "load_moves_history", return_value=[record]), \
                mock.patch.object(dev_cleaner, "is_junction", return_value=False), \
                mock.patch.object(dev_cleaner.ctk, "CTkFrame"), \
                mock.patch.object(dev_cleaner.ctk, "CTkFont"), \
                mock.patch.object(dev_cleaner.ctk, "CTkLabel") as labels, \
                mock.patch.object(dev_cleaner.ctk, "CTkButton") as buttons:
            app.refresh_restore_list()
        self.assertEqual(buttons.call_args.kwargs["text"], "Coba Bersihkan Target")
        self.assertTrue(any("pembersihan tertunda" in call.kwargs.get("text", "").lower()
                            for call in labels.call_args_list))

    def test_pending_cleanup_confirmation_submits_retry_not_restore(self):
        app = dev_cleaner.DevAICleanerApp.__new__(dev_cleaner.DevAICleanerApp)
        app.executor = mock.Mock()
        record = {"name": "Example", "original_path": "C:/Example", "target_path": "D:/Example",
                  "phase": "restored_pending_cleanup", "manifest": {}}
        with mock.patch.object(dev_cleaner, "is_user_admin", return_value=True), \
                mock.patch.object(dev_cleaner.messagebox, "askyesno", return_value=True), \
                mock.patch.object(dev_cleaner.psutil, "disk_usage") as usage:
            app.confirm_and_restore_app(record)
        app.executor.submit.assert_called_once_with(app._bg_retry_restore_cleanup, record)
        usage.assert_not_called()

    def test_pending_cleanup_retry_uses_durable_record_without_copying(self):
        with tempfile.TemporaryDirectory() as directory:
            orig = os.path.join(directory, "original")
            target = os.path.join(directory, "target")
            os.mkdir(orig)
            os.mkdir(target)
            with open(os.path.join(orig, "app.bin"), "wb") as file:
                file.write(b"safe data")
            record = {"name": "Example", "original_path": orig, "target_path": target,
                      "phase": "restored_pending_cleanup",
                      "manifest": dev_cleaner.directory_manifest(orig)}
            app = dev_cleaner.DevAICleanerApp.__new__(dev_cleaner.DevAICleanerApp)
            app.log = mock.Mock()
            app.after = mock.Mock()
            app.refresh_restore_list = mock.Mock()
            with mock.patch.object(dev_cleaner, "load_moves_history", return_value=[record]), \
                    mock.patch.object(dev_cleaner, "save_moves_history") as save, \
                    mock.patch.object(dev_cleaner.subprocess, "run") as run:
                app._bg_retry_restore_cleanup(record)
            self.assertFalse(os.path.lexists(target))
            self.assertTrue(os.path.isfile(os.path.join(orig, "app.bin")))
            save.assert_called_once_with([])
            run.assert_not_called()
            app.after.assert_called_once()

    def test_retry_history_failure_keeps_durable_record_after_target_removed(self):
        with tempfile.TemporaryDirectory() as directory:
            orig = os.path.join(directory, "original")
            target = os.path.join(directory, "target")
            os.mkdir(orig)
            os.mkdir(target)
            record = {"name": "Example", "original_path": orig, "target_path": target,
                      "phase": "restored_pending_cleanup", "manifest": {}}
            app = dev_cleaner.DevAICleanerApp.__new__(dev_cleaner.DevAICleanerApp)
            app.log = mock.Mock()
            app.after = mock.Mock()
            app.refresh_restore_list = mock.Mock()
            with mock.patch.object(dev_cleaner, "load_moves_history", return_value=[record]), \
                    mock.patch.object(dev_cleaner, "save_moves_history", side_effect=OSError("locked")):
                app._bg_retry_restore_cleanup(record)
            self.assertFalse(os.path.lexists(target))
            self.assertEqual(record["phase"], "restored_pending_cleanup")
            app.after.assert_not_called()
            with mock.patch.object(dev_cleaner, "load_moves_history", return_value=[record]), \
                    mock.patch.object(dev_cleaner, "save_moves_history") as save:
                app._bg_retry_restore_cleanup(record)
            save.assert_called_once_with([])
            app.after.assert_called_once()

    def test_verified_restore_reinserts_candidate_without_scan(self):
        with tempfile.TemporaryDirectory() as directory:
            app, record, save = self.run_restore(directory)
            self.assertFalse(os.path.exists(record["target_path"]))
            self.assertTrue(os.path.isfile(os.path.join(record["original_path"], "app.bin")))
            self.assertEqual(save.call_count, 2)
            self.assertEqual(save.call_args_list[0].args[0][0]["phase"], "restored_pending_cleanup")
            self.assertEqual(save.call_args_list[-1].args[0], [])
            for call in app.after.call_args_list:
                call.args[1]()
            self.assertEqual([item["path"] for item in app.app_items], [record["original_path"]])
            app._render_app_row.assert_called_once()


if __name__ == "__main__":
    unittest.main()
