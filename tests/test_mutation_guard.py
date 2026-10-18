import unittest
from unittest import mock

import dev_cleaner


class MutationGuardTests(unittest.TestCase):
    def make_app(self):
        app = dev_cleaner.DevAICleanerApp.__new__(dev_cleaner.DevAICleanerApp)
        app.tk = mock.Mock()
        app.active_mutation = None
        app.is_scanning_smart = False
        app.is_scanning_apps = False
        app.is_scanning_libs = False
        app.is_scanning_dup = False
        app.is_scanning_startup = False
        app.is_scanning_services = False
        app.log = mock.Mock()
        app.after = mock.Mock()
        app.executor = mock.Mock()
        return app

    def test_acquire_mutation_guard_succeeds_when_idle(self):
        app = self.make_app()
        self.assertTrue(app.acquire_mutation_guard("smart_clean"))
        self.assertEqual(app.active_mutation, "smart_clean")

    def test_acquire_mutation_guard_rejects_overlapping_mutation(self):
        app = self.make_app()
        self.assertTrue(app.acquire_mutation_guard("app_move"))
        self.assertFalse(app.acquire_mutation_guard("lib_uninstall"))
        self.assertEqual(app.active_mutation, "app_move")
        self.assertTrue(any("sedang berlangsung" in str(call.args[0]) for call in app.log.call_args_list))

    def test_acquire_mutation_guard_rejects_when_conflicting_scan_active(self):
        app = self.make_app()
        app.is_scanning_smart = True
        self.assertFalse(app.acquire_mutation_guard("smart_clean"))
        self.assertIsNone(app.active_mutation)

    def test_release_mutation_guard_resets_active_mutation(self):
        app = self.make_app()
        self.assertTrue(app.acquire_mutation_guard("dup_delete"))
        app.release_mutation_guard()
        self.assertIsNone(app.active_mutation)
        self.assertTrue(app.acquire_mutation_guard("service_toggle"))

    def test_scans_are_blocked_while_mutation_active(self):
        app = self.make_app()
        app.active_mutation = "app_move"
        app.subcat_vars = {}
        app.dup_target_dir = "C:\\dummy"
        app.smart_scroll = mock.Mock()
        app.move_scroll = mock.Mock()
        app.lib_scroll = mock.Mock()
        app.dup_scroll = mock.Mock()
        app.startup_scroll = mock.Mock()
        app.svc_scroll = mock.Mock()

        # Test smart scan rejection
        app.start_smart_scan_async()
        app.executor.submit.assert_not_called()

        # Test apps scan rejection
        app.scan_installed_apps_async()
        app.executor.submit.assert_not_called()

        # Test libs scan rejection
        app._get_active_python_exe = mock.Mock(return_value="python.exe")
        app.scan_libs_async()
        app.executor.submit.assert_not_called()

        # Test dup scan rejection
        app.start_dup_scan_async()
        app.executor.submit.assert_not_called()

        # Test startup scan rejection
        app.scan_startup_items_async()
        app.executor.submit.assert_not_called()

        # Test services scan rejection
        app.scan_services_async()
        app.executor.submit.assert_not_called()

    def test_lib_uninstall_guard_lifecycle(self):
        app = self.make_app()
        item = {"name": "test-lib", "is_core": False, "var": mock.Mock(get=mock.Mock(return_value=True)),
                "python_exe": "python.exe", "row_widget": mock.Mock()}
        app.lib_items = [item]
        with mock.patch.object(dev_cleaner.messagebox, "askyesno", return_value=True):
            app.confirm_and_uninstall_libs()
        self.assertEqual(app.active_mutation, "lib_uninstall")
        app.executor.submit.assert_called_once()
        bg_func = app.executor.submit.call_args[0][0]

        with mock.patch.object(dev_cleaner.subprocess, "run", return_value=mock.Mock(returncode=0, stdout="false", stderr="")), \
                mock.patch.object(dev_cleaner, "log_py_debug"):
            bg_func([item], "python.exe")

        # After worker finishes, scheduled UI callback releases guard
        self.assertEqual(app.after.call_count, 1)
        ui_callback = app.after.call_args[0][1]
        ui_callback()
        self.assertIsNone(app.active_mutation)

    def test_dup_delete_guard_lifecycle(self):
        app = self.make_app()
        app.btn_dup_delete = mock.Mock()
        app._render_all_dup_groups = mock.Mock()
        item = {"name": "dup.txt", "path": "C:\\dup.txt", "size_bytes": 100, "var": mock.Mock(get=mock.Mock(return_value=True))}
        app.dup_items = [item]
        app.dup_groups = [{"items": [item]}]
        with mock.patch.object(dev_cleaner.messagebox, "askyesno", return_value=True):
            app.confirm_and_delete_duplicates()
        self.assertEqual(app.active_mutation, "dup_delete")
        app.executor.submit.assert_called_once()
        bg_func = app.executor.submit.call_args[0][0]

        with mock.patch.object(dev_cleaner.os.path, "exists", side_effect=[True, False]), \
                mock.patch.object(dev_cleaner, "send2trash"):
            bg_func([item])

        self.assertEqual(app.after.call_count, 1)
        ui_callback = app.after.call_args[0][1]
        ui_callback()
        self.assertIsNone(app.active_mutation)

    def test_startup_toggle_guard_lifecycle(self):
        app = self.make_app()
        item = {"name": "test_app", "is_enabled": False, "root_h": mock.Mock(),
                "status_widget": mock.Mock(), "action_widget": mock.Mock()}
        with mock.patch.object(dev_cleaner.winreg, "OpenKey"), \
                mock.patch.object(dev_cleaner.winreg, "SetValueEx"), \
                mock.patch.object(dev_cleaner.winreg, "QueryValueEx", return_value=(b'\x02' + bytes(11), dev_cleaner.winreg.REG_BINARY)):
            app.toggle_startup_state(item)
        self.assertIsNone(app.active_mutation)
        self.assertTrue(item["is_enabled"])

    def test_service_toggle_guard_lifecycle(self):
        app = self.make_app()
        item = {"name": "test_svc", "status": "stopped", "status_widget": mock.Mock(), "action_widget": mock.Mock()}
        app.toggle_service_state(item)
        self.assertEqual(app.active_mutation, "service_toggle")
        app.executor.submit.assert_called_once()
        bg_func = app.executor.submit.call_args[0][0]

        with mock.patch.object(dev_cleaner.subprocess, "run", return_value=mock.Mock(returncode=0, stdout="", stderr="")), \
                mock.patch.object(dev_cleaner.psutil, "win_service_get", return_value=mock.Mock(status=mock.Mock(return_value="running"))):
            bg_func()

        self.assertIsNone(app.active_mutation)


if __name__ == "__main__":
    unittest.main()
