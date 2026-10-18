import os
import shutil
import tempfile
import unittest
from unittest import mock

import dev_cleaner


class AppMoverMoveTests(unittest.TestCase):
    def run_move(self, directory, collision=False, corrupt=False, junction=True, history_error=False, rollback_error=False):
        source = os.path.join(directory, "Example")
        root = os.path.join(directory, "destination")
        destination = os.path.join(root, "Example")
        os.mkdir(source)
        os.mkdir(root)
        with open(os.path.join(source, "app.bin"), "wb") as file:
            file.write(b"original")
        if collision:
            os.mkdir(destination)
            with open(os.path.join(destination, "unrelated.bin"), "wb") as file:
                file.write(b"keep")
        item = {"name": "Example", "path": source, "size_bytes": 8, "row_widget": mock.Mock()}
        app = dev_cleaner.DevAICleanerApp.__new__(dev_cleaner.DevAICleanerApp)
        app.app_items = [item]
        app.log = mock.Mock()
        app.after = mock.Mock()
        app.btn_move_apps = mock.Mock()
        app.refresh_restore_list = mock.Mock()
        linked = set()
        rename = os.rename
        def checked_rename(src, dest):
            if rollback_error and os.path.basename(src) == "original":
                raise OSError("rollback locked")
            return rename(src, dest)
        def command(args, **kwargs):
            if args[0] == "robocopy":
                shutil.copytree(args[1], args[2], dirs_exist_ok=True)
                if corrupt:
                    with open(os.path.join(args[2], "app.bin"), "wb") as file:
                        file.write(b"corrupt")
            elif junction:
                os.mkdir(args[-2])
                linked.add(args[-2])
            return mock.Mock(returncode=0, stdout="", stderr="")
        with mock.patch.object(dev_cleaner, "load_moves_history", return_value=[]), \
                mock.patch.object(dev_cleaner, "save_moves_history", side_effect=OSError("history locked") if history_error else None) as save, \
                mock.patch.object(dev_cleaner, "stop_processes_in_folder"), \
                mock.patch.object(dev_cleaner.os, "rename", side_effect=checked_rename), \
                mock.patch.object(dev_cleaner, "is_junction", side_effect=lambda path: path in linked), \
                mock.patch.object(dev_cleaner.os.path, "samefile", return_value=True), \
                mock.patch.object(dev_cleaner.subprocess, "run", side_effect=command) as run, \
                mock.patch.object(dev_cleaner.messagebox, "showinfo"), \
                mock.patch.object(dev_cleaner.messagebox, "showerror"):
            app._bg_move_apps([item], root)
            for call in app.after.call_args_list:
                call.args[1]()
        return app, item, destination, save, run

    def test_existing_destination_is_never_modified(self):
        with tempfile.TemporaryDirectory() as directory:
            app, item, destination, save, run = self.run_move(directory, collision=True)
            self.assertTrue(os.path.isfile(os.path.join(destination, "unrelated.bin")))
            self.assertFalse(os.path.exists(os.path.join(destination, "app.bin")))
            run.assert_not_called()
            self.assertEqual(app.app_items, [item])

    def test_corrupt_copy_preserves_original_and_row(self):
        with tempfile.TemporaryDirectory() as directory:
            app, item, destination, save, run = self.run_move(directory, corrupt=True)
            with open(os.path.join(item["path"], "app.bin"), "rb") as file:
                self.assertEqual(file.read(), b"original")
            save.assert_not_called()
            self.assertEqual(app.app_items, [item])

    def test_unverified_junction_rolls_back_original(self):
        with tempfile.TemporaryDirectory() as directory:
            app, item, destination, save, run = self.run_move(directory, junction=False)
            self.assertTrue(os.path.isfile(os.path.join(item["path"], "app.bin")))
            save.assert_not_called()
            self.assertEqual(app.app_items, [item])

    def test_history_failure_retains_backup_and_row(self):
        with tempfile.TemporaryDirectory() as directory:
            app, item, destination, save, run = self.run_move(directory, history_error=True)
            self.assertEqual(app.app_items, [item])
            backups = [os.path.join(root, name) for root, dirs, files in os.walk(directory)
                       for name in files if name == "app.bin"]
            self.assertGreaterEqual(len(backups), 2)
            item["row_widget"].destroy.assert_not_called()

    def test_failed_rollback_preserves_backup_and_reports_its_location(self):
        with tempfile.TemporaryDirectory() as directory:
            app, item, destination, save, run = self.run_move(
                directory, history_error=True, rollback_error=True)
            backups = [os.path.join(directory, name, "original", "app.bin")
                       for name in os.listdir(directory) if name.startswith(".mover-backup-")]
            self.assertEqual(len(backups), 1)
            self.assertTrue(os.path.isfile(backups[0]))
            self.assertTrue(os.path.isfile(os.path.join(destination, "app.bin")))
            self.assertEqual(app.app_items, [item])
            self.assertTrue(any("ERROR rollback" in call.args[0] for call in app.log.call_args_list))

    def test_verified_move_updates_ui_only_after_history_saved(self):
        with tempfile.TemporaryDirectory() as directory:
            app, item, destination, save, run = self.run_move(directory)
            self.assertEqual(app.app_items, [])
            item["row_widget"].destroy.assert_called_once()
            save.assert_called_once()
            for call in run.call_args_list:
                self.assertEqual(call.kwargs["creationflags"], dev_cleaner.hidden_console_creation_flags())


if __name__ == "__main__":
    unittest.main()
