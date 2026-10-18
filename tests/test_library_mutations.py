import unittest
from unittest import mock

import dev_cleaner


class LibraryUninstallTests(unittest.TestCase):
    def run_uninstall(self, pip_code, verify_code, output):
        app = dev_cleaner.DevAICleanerApp.__new__(dev_cleaner.DevAICleanerApp)
        item = {"name": "example-pkg", "row_widget": mock.Mock()}
        app.lib_items = [item]
        app.log = mock.Mock()
        app.after = mock.Mock(side_effect=lambda delay, callback: callback())
        app.ent_lib_search = mock.Mock()
        app.filter_libs = mock.Mock()
        app.scan_libs_async = mock.Mock()
        results = [mock.Mock(returncode=pip_code, stdout="", stderr=""),
                   mock.Mock(returncode=verify_code, stdout=output, stderr="")]
        with mock.patch.object(dev_cleaner.subprocess, "run", side_effect=results) as run, \
                mock.patch.object(dev_cleaner, "log_py_debug"):
            app._bg_uninstall_libs([item], "selected-python.exe")
        app.scan_libs_async.assert_not_called()
        for call in run.call_args_list:
            self.assertEqual(call.args[0][0], "selected-python.exe")
            self.assertEqual(call.kwargs["creationflags"], dev_cleaner.hidden_console_creation_flags())
        return app, item

    def test_verification_process_error_does_not_mean_absent(self):
        app, item = self.run_uninstall(0, 1, "")
        self.assertEqual(app.lib_items, [item])
        item["row_widget"].destroy.assert_not_called()

    def test_success_requires_explicit_absence_output(self):
        app, item = self.run_uninstall(0, 0, "false\n")
        self.assertEqual(app.lib_items, [])
        item["row_widget"].destroy.assert_called_once()

    def test_failed_pip_keeps_row_even_if_verification_reports_absence(self):
        app, item = self.run_uninstall(1, 0, "false\n")
        self.assertEqual(app.lib_items, [item])

    def test_present_package_keeps_row(self):
        app, item = self.run_uninstall(0, 0, "true\n")
        self.assertEqual(app.lib_items, [item])


class LibraryEnvironmentTests(unittest.TestCase):
    def test_missing_selected_interpreter_does_not_fall_back(self):
        app = dev_cleaner.DevAICleanerApp.__new__(dev_cleaner.DevAICleanerApp)
        app.cmb_py_env = mock.Mock()
        app.cmb_py_env.get.return_value = "selected"
        app.py_envs = {"selected": "missing.exe", "other": "other.exe"}
        with mock.patch.object(dev_cleaner.os.path, "exists", side_effect=lambda path: path == "other.exe"):
            self.assertIsNone(app._get_active_python_exe())

    def test_uninstall_does_not_remove_replacement_row_from_another_environment(self):
        app = dev_cleaner.DevAICleanerApp.__new__(dev_cleaner.DevAICleanerApp)
        selected = {"name": "example-pkg", "python_exe": "selected.exe", "row_widget": mock.Mock()}
        replacement = {"name": "example-pkg", "python_exe": "other.exe", "row_widget": mock.Mock()}
        app.lib_items = [replacement]
        app.log = mock.Mock()
        app.after = mock.Mock(side_effect=lambda delay, callback: callback())
        app.ent_lib_search = mock.Mock()
        app.filter_libs = mock.Mock()
        with mock.patch.object(dev_cleaner.subprocess, "run", return_value=mock.Mock(returncode=0, stdout="false", stderr="")), \
                mock.patch.object(dev_cleaner, "log_py_debug"):
            app._bg_uninstall_libs([selected], "selected.exe")
        self.assertEqual(app.lib_items, [replacement])
        replacement["row_widget"].destroy.assert_not_called()

    def test_scan_submission_preserves_existing_rows_and_captures_interpreter(self):
        app = dev_cleaner.DevAICleanerApp.__new__(dev_cleaner.DevAICleanerApp)
        app.is_scanning_libs = False
        app.btn_scan_libs = mock.Mock()
        app.log = mock.Mock()
        app.lib_scroll = mock.Mock()
        app.lib_scroll.winfo_children.return_value = []
        previous = {"name": "existing"}
        app.lib_items = [previous]
        app._get_active_python_exe = mock.Mock(return_value="selected.exe")
        app.executor = mock.Mock()
        app.scan_libs_async()
        self.assertEqual(app.lib_items, [previous])
        app.lib_scroll.winfo_children.assert_not_called()
        app.executor.submit.assert_called_once_with(app._bg_scan_libs, "selected.exe")


class LibraryScanTests(unittest.TestCase):
    def test_failed_scan_preserves_previous_rows(self):
        app = dev_cleaner.DevAICleanerApp.__new__(dev_cleaner.DevAICleanerApp)
        previous = {"name": "existing", "row_widget": mock.Mock()}
        app.lib_items = [previous]
        app.log = mock.Mock()
        app.after = mock.Mock(side_effect=lambda delay, callback: callback())
        app.btn_scan_libs = mock.Mock()
        with mock.patch.object(dev_cleaner.os.path, "exists", return_value=True), \
                mock.patch.object(dev_cleaner, "log_py_debug"), \
                mock.patch.object(dev_cleaner.subprocess, "run", return_value=mock.Mock(returncode=1, stdout="", stderr="failed")):
            app._bg_scan_libs("selected.exe")
        self.assertEqual(app.lib_items, [previous])
        previous["row_widget"].destroy.assert_not_called()

    def test_empty_selected_environment_never_falls_back_to_host_packages(self):
        app = dev_cleaner.DevAICleanerApp.__new__(dev_cleaner.DevAICleanerApp)
        app._get_active_python_exe = mock.Mock(return_value="selected-python.exe")
        app.log = mock.Mock()
        app.after = mock.Mock(side_effect=lambda delay, callback: callback())
        app.btn_scan_libs = mock.Mock()
        app.lib_items = []
        app._render_lib_row = mock.Mock()
        app.lib_scroll = mock.Mock()
        app.lib_scroll.winfo_children.return_value = []
        with mock.patch.object(dev_cleaner.os.path, "exists", return_value=True), \
                mock.patch.object(dev_cleaner, "log_py_debug"), \
                mock.patch.object(dev_cleaner.importlib.metadata, "distributions", return_value=[]) as host_scan, \
                mock.patch.object(dev_cleaner.subprocess, "run", return_value=mock.Mock(returncode=0, stdout="[]", stderr="")) as run:
            app._bg_scan_libs("selected-python.exe")
        host_scan.assert_not_called()
        self.assertEqual(app.lib_items, [])
        self.assertEqual(run.call_args.kwargs["creationflags"], dev_cleaner.hidden_console_creation_flags())


if __name__ == "__main__":
    unittest.main()
