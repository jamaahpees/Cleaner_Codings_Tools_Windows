"""Publication regressions without invoking installers or reading the real registry."""
import inspect
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, mock_open, patch

import dev_cleaner as ui


class PublicReadinessTests(unittest.TestCase):
    def test_neutral_visible_branding(self):
        source = inspect.getsource(ui)
        for old in ('CCleaner', 'WinUP', 'Ghost Toolbox'):
            self.assertNotIn(old, source)
        self.assertIn('System Toolbox (Tweaks & Tools)', source)

    def test_legacy_patch_metadata_has_no_execution_path(self):
        source = inspect.getsource(ui.DevAICleanerApp)
        for removed in ('crack_dir', 'Menerapkan Crack', 'Auto-Crack', 'Easeware'):
            self.assertNotIn(removed, source)
        self.assertIn('if returncode == 0:', source)

    def test_installer_ignores_legacy_patch_metadata(self):
        for kind, code in (('exe', 0), ('msi', 0), ('exe', 1)):
            with self.subTest(kind=kind, returncode=code):
                app = SimpleNamespace(
                    _get_cleaner_downloads_dir=Mock(return_value='C:/Demo/Downloads'),
                    native_app_status_labels={}, native_app_buttons={},
                    native_app_cancel_buttons={}, active_download_cancellations={},
                    active_installer_processes={}, log=Mock(),
                    _scan_installed_registry_apps=Mock(return_value={}),
                    _filter_native_apps=Mock(), executor=Mock(),
                    after=lambda delay, callback: callback())
                app.executor.submit.side_effect = lambda worker: worker()
                process = Mock(returncode=code)
                process.communicate.return_value = (b'', b'')
                item = dict(id='demo', name='Demo', filename='setup.exe', type=kind,
                            local_setup='C:/Demo/setup.exe', crack_dir='C:/Demo/legacy',
                            silent_args='/quiet')
                with patch.object(ui.os.path, 'exists', return_value=True), \
                        patch.object(ui.subprocess, 'Popen', return_value=process) as launch, \
                        patch.object(ui.psutil, 'process_iter') as enumerate_processes, \
                        patch.object(ui.shutil, 'copy2') as copy, \
                        patch.object(ui.urllib.request, 'urlopen') as network, \
                        patch.object(ui.messagebox, 'showinfo') as success:
                    ui.DevAICleanerApp._download_and_install_native_app_async(app, item)
                    launch.assert_called_once()
                    self.assertEqual('msiexec.exe' in launch.call_args.args[0], kind == 'msi')
                    enumerate_processes.assert_not_called()
                    copy.assert_not_called()
                    network.assert_not_called()
                    self.assertEqual(success.call_count, int(code == 0))
                app._scan_installed_registry_apps.assert_called_once()
                app._filter_native_apps.assert_called_once()
                self.assertEqual(app.active_installer_processes, {})

    def load_catalog(self, exists, payload=None):
        app = SimpleNamespace(native_app_data=[{'name': 'stale'}], log=Mock(),
                              _scan_installed_registry_apps=Mock(return_value={}),
                              _render_native_apps=Mock())
        with patch.object(ui.os.path, 'exists', return_value=exists) as probe, \
                patch('builtins.open', mock_open(read_data=payload or '')):
            ui.DevAICleanerApp._load_native_catalog(app)
        expected = str(Path(ui.__file__).resolve().parent / 'app_catalog.json')
        for call in probe.call_args_list:
            self.assertEqual(str(Path(call.args[0])), expected)
        return app

    def test_missing_catalog_clears_previous_entries_without_private_fallback(self):
        app = self.load_catalog(False)
        self.assertEqual(app.native_app_data, [])
        app._render_native_apps.assert_called_once_with([])

    def test_malformed_catalog_clears_previous_entries(self):
        for payload in ('{', '{}', '[1]', 'null'):
            with self.subTest(payload=payload):
                app = self.load_catalog(True, payload)
                self.assertEqual(app.native_app_data, [])
                app.log.assert_called()

    def test_valid_catalog_is_rendered(self):
        app = self.load_catalog(True, '[{"id":"demo","name":"Demo"}]')
        app._render_native_apps.assert_called_once_with([{'id': 'demo', 'name': 'Demo'}])

    def test_launcher_installs_runtime_dependencies_and_checks_status(self):
        bat = (Path(ui.__file__).parent / 'Run-Dev-Cleaner.bat').read_text()
        self.assertIn('ttkbootstrap', bat)
        self.assertIn('psutil', bat)
        self.assertIn('if errorlevel 1', bat.lower())


if __name__ == '__main__':
    unittest.main()
