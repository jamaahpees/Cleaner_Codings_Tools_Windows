import json
import os
import tempfile
import unittest
from unittest import mock

import dev_cleaner


class StartupScanPreferenceTests(unittest.TestCase):
    def test_missing_preference_defaults_to_disabled(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "preferences.json")
            self.assertFalse(dev_cleaner.load_startup_scan_preference(path))

    def test_saved_preference_is_loaded(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "preferences.json")
            self.assertTrue(dev_cleaner.save_startup_scan_preference(path, True))
            self.assertTrue(dev_cleaner.load_startup_scan_preference(path))

    def test_malformed_preference_defaults_to_disabled(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "preferences.json")
            with open(path, "w", encoding="utf-8") as prefs:
                prefs.write("not json")
            self.assertFalse(dev_cleaner.load_startup_scan_preference(path))

    def test_write_failure_is_reported_without_raising(self):
        with mock.patch("builtins.open", side_effect=OSError("denied")):
            self.assertFalse(dev_cleaner.save_startup_scan_preference("prefs.json", True))


class SubprocessFlagsTests(unittest.TestCase):
    def test_windows_console_processes_get_hidden_creation_flag(self):
        with mock.patch.object(dev_cleaner.os, "name", "nt"):
            flags = dev_cleaner.hidden_console_creation_flags()
        self.assertEqual(flags, dev_cleaner.subprocess.CREATE_NO_WINDOW)

    def test_non_windows_processes_keep_default_creation_flags(self):
        with mock.patch.object(dev_cleaner.os, "name", "posix"):
            self.assertEqual(dev_cleaner.hidden_console_creation_flags(), 0)


class StartupDispatchTests(unittest.TestCase):
    def make_app(self, enabled):
        app = dev_cleaner.DevAICleanerApp.__new__(dev_cleaner.DevAICleanerApp)
        app.startup_scan_var = mock.Mock()
        app.startup_scan_var.get.return_value = enabled
        app.start_smart_scan_async = mock.Mock()
        app.log = mock.Mock()
        app.after = mock.Mock(side_effect=lambda delay, callback: callback())
        return app

    def test_startup_dispatch_runs_existing_scan_once_when_enabled(self):
        app = self.make_app(True)
        app.auto_initial_scan()
        app.auto_initial_scan()
        app.start_smart_scan_async.assert_called_once_with()

    def test_startup_dispatch_does_not_scan_when_disabled(self):
        app = self.make_app(False)
        app.auto_initial_scan()
        app.start_smart_scan_async.assert_not_called()


class SmartScanCategoryTests(unittest.TestCase):
    def test_scan_submits_plain_category_snapshot_to_existing_executor(self):
        app = dev_cleaner.DevAICleanerApp.__new__(dev_cleaner.DevAICleanerApp)
        app.is_scanning_smart = False
        app.log = mock.Mock()
        app.smart_scroll = mock.Mock()
        app.smart_scroll.winfo_children.return_value = []
        app.smart_findings = []
        app.update_smart_summary = mock.Mock()
        app.scan_progress_bar = mock.Mock()
        app.lbl_scan_status = mock.Mock()
        app.btn_smart_scan = mock.Mock()
        app._animate_scan_processing = mock.Mock()
        app.executor = mock.Mock()
        app.subcat_vars = {"chrome_cache": mock.Mock(), "reg_orphans": mock.Mock()}
        app.subcat_vars["chrome_cache"].get.return_value = True
        app.subcat_vars["reg_orphans"].get.return_value = False
        app.start_smart_scan_async()
        app.executor.submit.assert_called_once_with(app._bg_smart_scan,
                                                   {"chrome_cache": True, "reg_orphans": False})

    def test_registry_categories_are_filtered_independently_without_tk_access(self):
        app = dev_cleaner.DevAICleanerApp.__new__(dev_cleaner.DevAICleanerApp)
        app.after = mock.Mock()
        with mock.patch.object(dev_cleaner, "scan_registry_orphans", return_value=[
                {"type": "reg_app_path"}, {"type": "reg_uninstall"}]), \
                mock.patch.object(dev_cleaner.tk, "BooleanVar") as tk_var:
            app._bg_smart_scan({"reg_app_paths": True})
        self.assertEqual(app.smart_findings, [{"type": "reg_app_path"}])
        tk_var.assert_not_called()


class SmartCleanerMutationTests(unittest.TestCase):
    def test_missing_selected_folder_remains_in_findings(self):
        app = dev_cleaner.DevAICleanerApp.__new__(dev_cleaner.DevAICleanerApp)
        row = mock.Mock()
        finding = {"type": "folder", "path": "missing-folder", "name": "Missing", "size_bytes": 1, "row_widget": row}
        app.smart_findings = [finding]
        app.btn_clean_smart = mock.Mock()
        app.log = mock.Mock()
        app.update_smart_summary = mock.Mock()
        app.after = mock.Mock()
        app.smart_scroll = mock.Mock()

        with mock.patch.object(dev_cleaner.os.path, "exists", return_value=False):
            app._bg_clean_smart([finding])

        callback = app.after.call_args.args[1]
        callback()
        self.assertEqual(app.smart_findings, [finding])
        row.destroy.assert_not_called()

    def test_partial_folder_cleanup_keeps_finding_when_one_child_fails(self):
        app = dev_cleaner.DevAICleanerApp.__new__(dev_cleaner.DevAICleanerApp)
        row = mock.Mock()
        finding = {"type": "folder_contents", "path": "temp-folder", "name": "Temp", "size_bytes": 8, "row_widget": row}
        app.smart_findings = [finding]
        app.btn_clean_smart = mock.Mock()
        app.log = mock.Mock()
        app.update_smart_summary = mock.Mock()
        app.smart_scroll = mock.Mock()
        app.after = mock.Mock()
        entry = mock.Mock()
        entry.is_file.return_value = True
        entry.path = "temp-folder/locked.tmp"
        with mock.patch.object(dev_cleaner.os.path, "exists", return_value=True), \
                mock.patch.object(dev_cleaner.os, "scandir", return_value=[entry]), \
                mock.patch.object(dev_cleaner.os, "remove", side_effect=PermissionError("locked")):
            app._bg_clean_smart([finding])

        app.after.call_args.args[1]()
        self.assertEqual(app.smart_findings, [finding])
        row.destroy.assert_not_called()
        app.log.assert_any_call("Peringatan saat membersihkan Temp: locked")

    def test_startup_scan_checkbox_uses_persisted_dispatch_variable(self):
        class FakeWidget:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

            def pack(self, **kwargs):
                pass

            def pack_propagate(self, *args):
                pass

            def set(self, *args):
                pass

        class WidgetFactory:
            def __init__(self):
                self.calls = []

            def __call__(self, *args, **kwargs):
                widget = FakeWidget(**kwargs)
                self.calls.append(widget)
                return widget

        app = dev_cleaner.DevAICleanerApp.__new__(dev_cleaner.DevAICleanerApp)
        preference_var = object()
        app.startup_scan_var = preference_var
        checkbox_factory = WidgetFactory()
        with mock.patch.object(dev_cleaner.tk, "BooleanVar", new=lambda **kwargs: preference_var), \
                mock.patch.object(dev_cleaner.ctk, "CTkFrame", new=WidgetFactory()), \
                mock.patch.object(dev_cleaner.ctk, "CTkButton", new=WidgetFactory()), \
                mock.patch.object(dev_cleaner.ctk, "CTkLabel", new=WidgetFactory()), \
                mock.patch.object(dev_cleaner.ctk, "CTkProgressBar", new=WidgetFactory()), \
                mock.patch.object(dev_cleaner.ctk, "CTkScrollableFrame", new=WidgetFactory()), \
                mock.patch.object(dev_cleaner.ctk, "CTkFont", new=lambda **kwargs: kwargs), \
                mock.patch.object(dev_cleaner.ctk, "CTkCheckBox", new=checkbox_factory):
            app.views = {"smart_cleaner": FakeWidget()}
            app._show_smart_idle_placeholder = lambda: None
            app.setup_smart_cleaner_view()

        startup_checkbox = next(widget for widget in checkbox_factory.calls
                                if widget.kwargs.get("text") == "Pindai otomatis saat dibuka")
        self.assertIs(app.startup_scan_var, preference_var)
        self.assertIs(startup_checkbox.kwargs["variable"], preference_var)
        self.assertIs(app.chk_startup_scan, startup_checkbox)


class StartupMutationTests(unittest.TestCase):
    def test_toggle_reads_back_written_value_without_rescan(self):
        self.check_toggle(b'\x03' + bytes(11), False)

    def test_failed_verification_keeps_original_status(self):
        self.check_toggle(b'\x02' + bytes(11), True)

    def check_toggle(self, readback, expected):
        app = dev_cleaner.DevAICleanerApp.__new__(dev_cleaner.DevAICleanerApp)
        app.log = mock.Mock()
        app.scan_startup_items_async = mock.Mock()
        item = {"name": "Example", "root_h": dev_cleaner.winreg.HKEY_CURRENT_USER,
                "is_enabled": True, "status_widget": mock.Mock(), "action_widget": mock.Mock()}
        with mock.patch.object(dev_cleaner.winreg, "OpenKey", return_value=mock.MagicMock()), \
                mock.patch.object(dev_cleaner.winreg, "SetValueEx"), \
                mock.patch.object(dev_cleaner.winreg, "QueryValueEx", return_value=(readback, dev_cleaner.winreg.REG_BINARY)), \
                mock.patch.object(dev_cleaner.messagebox, "showerror"):
            app.toggle_startup_state(item)
        self.assertEqual(item["is_enabled"], expected)
        app.scan_startup_items_async.assert_not_called()
        if expected:
            item["status_widget"].configure.assert_not_called()
        else:
            item["status_widget"].configure.assert_called_once()


class ServiceMutationTests(unittest.TestCase):
    def test_service_status_changes_only_on_successful_sc_command(self):
        app = dev_cleaner.DevAICleanerApp.__new__(dev_cleaner.DevAICleanerApp)
        item = {"name": "ExampleSvc", "status": "running"}
        submitted = []
        app.executor = mock.Mock()
        app.executor.submit.side_effect = lambda fn: submitted.append(fn)
        app.log = mock.Mock()
        app.after = mock.Mock(side_effect=lambda delay, callback: callback())

        with mock.patch.object(dev_cleaner.psutil, "win_service_get") as service, \
                mock.patch.object(dev_cleaner.subprocess, "run", return_value=mock.Mock(returncode=0, stdout="", stderr="")) as run:
            service.return_value.status.return_value = "stopped"
            app.toggle_service_state(item)
            submitted[0]()

        run.assert_called_once()
        self.assertEqual(item["status"], "stopped")
        app.log.assert_any_call("Layanan 'ExampleSvc' berhasil di-stop!")

    def test_successful_command_with_pending_service_keeps_row_unchanged(self):
        app = dev_cleaner.DevAICleanerApp.__new__(dev_cleaner.DevAICleanerApp)
        item = {"name": "ExampleSvc", "status": "running"}
        app.executor = mock.Mock()
        app.executor.submit.side_effect = lambda fn: fn()
        app.log = mock.Mock()
        app.after = mock.Mock(side_effect=lambda delay, callback: callback())
        with mock.patch.object(dev_cleaner.psutil, "win_service_get") as service, \
                mock.patch.object(dev_cleaner.subprocess, "run", return_value=mock.Mock(returncode=0)):
            service.return_value.status.return_value = "stop_pending"
            app.toggle_service_state(item)
        self.assertEqual(item["status"], "running")

    def test_failed_service_command_preserves_status(self):
        app = dev_cleaner.DevAICleanerApp.__new__(dev_cleaner.DevAICleanerApp)
        item = {"name": "ExampleSvc", "status": "running"}
        submitted = []
        app.executor = mock.Mock()
        app.executor.submit.side_effect = lambda fn: submitted.append(fn)
        app.log = mock.Mock()
        app.after = mock.Mock(side_effect=lambda delay, callback: callback())

        with mock.patch.object(dev_cleaner.subprocess, "run", return_value=mock.Mock(returncode=5, stdout="access denied", stderr="")):
            app.toggle_service_state(item)
            submitted[0]()

        self.assertEqual(item["status"], "running")


if __name__ == "__main__":
    unittest.main()
