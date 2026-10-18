import os
import tempfile
import unittest
from unittest import mock

import dev_cleaner


class RegistryBackupTests(unittest.TestCase):
    def test_backup_contains_exported_values_and_nested_keys(self):
        item = {"root_str": "HKEY_CURRENT_USER", "sub_path": r"Software\Example"}
        exported = 'Windows Registry Editor Version 5.00\n\n[HKEY_CURRENT_USER\\Software\\Example]\n"Name"="Example"\n\n[HKEY_CURRENT_USER\\Software\\Example\\Child]\n"Count"=dword:00000001\n'
        def export(command, **kwargs):
            self.assertEqual(command[:2], ["reg.exe", "export"])
            self.assertEqual(command[2], r"HKEY_CURRENT_USER\Software\Example")
            self.assertEqual(kwargs["creationflags"], dev_cleaner.hidden_console_creation_flags())
            with open(command[3], "w", encoding="utf-16") as file:
                file.write(exported)
            return mock.Mock(returncode=0, stdout="", stderr="")
        with tempfile.TemporaryDirectory() as directory, \
                mock.patch.object(dev_cleaner, "REG_BACKUP_DIR", directory), \
                mock.patch.object(dev_cleaner.subprocess, "run", side_effect=export):
            backup = dev_cleaner.create_registry_backup([item])
            with open(backup, encoding="utf-16") as file:
                self.assertEqual(file.read(), exported)

    def test_success_exit_without_export_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory, \
                mock.patch.object(dev_cleaner, "REG_BACKUP_DIR", directory), \
                mock.patch.object(dev_cleaner.subprocess, "run", return_value=mock.Mock(returncode=0)):
            self.assertIsNone(dev_cleaner.create_registry_backup([
                {"root_str": "HKEY_CURRENT_USER", "sub_path": r"Software\Example"}]))

    def test_failed_export_does_not_authorize_deletion(self):
        with tempfile.TemporaryDirectory() as directory, \
                mock.patch.object(dev_cleaner, "REG_BACKUP_DIR", directory), \
                mock.patch.object(dev_cleaner.subprocess, "run", return_value=mock.Mock(returncode=1, stdout="", stderr="denied")):
            self.assertIsNone(dev_cleaner.create_registry_backup([
                {"root_str": "HKEY_CURRENT_USER", "sub_path": r"Software\Example"}]))


class RegistryDeleteTests(unittest.TestCase):
    def test_delete_requires_verified_absence(self):
        for absent in (False, True):
            with self.subTest(absent=absent):
                app = dev_cleaner.DevAICleanerApp.__new__(dev_cleaner.DevAICleanerApp)
                item = {"type": "reg_app_path", "root": dev_cleaner.winreg.HKEY_CURRENT_USER,
                        "sub_path": r"Software\Example", "name": "Example", "row_widget": mock.Mock()}
                app.smart_findings = [item]
                app.smart_scroll = mock.Mock()
                app.log = mock.Mock()
                app.after = mock.Mock()
                app.btn_clean_smart = mock.Mock()
                app.update_smart_summary = mock.Mock()
                parent = mock.MagicMock()
                verification = FileNotFoundError("absent") if absent else mock.MagicMock()
                with mock.patch.object(dev_cleaner, "create_registry_backup", return_value="backup.reg"), \
                        mock.patch.object(dev_cleaner.winreg, "OpenKey", side_effect=[parent, verification]) as opened, \
                        mock.patch.object(dev_cleaner.winreg, "DeleteKey") as delete, \
                        mock.patch.object(dev_cleaner.ctk, "CTkLabel"), \
                        mock.patch.object(dev_cleaner.ctk, "CTkFont"):
                    app._bg_clean_smart([item])
                    app.after.call_args.args[1]()
                delete.assert_called_once_with(parent.__enter__.return_value, "Example")
                self.assertEqual(opened.call_args_list[0].args[1], "Software")
                self.assertEqual(app.smart_findings, [] if absent else [item])


if __name__ == "__main__":
    unittest.main()
