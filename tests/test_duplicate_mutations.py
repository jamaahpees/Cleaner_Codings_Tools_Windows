import unittest
from unittest import mock

import dev_cleaner


class DuplicateMutationTests(unittest.TestCase):
    def test_successful_delete_retains_failed_singleton_in_both_collections(self):
        app = dev_cleaner.DevAICleanerApp.__new__(dev_cleaner.DevAICleanerApp)
        removed = {"path": "removed.bin", "size_bytes": 8}
        failed = {"path": "locked.bin", "size_bytes": 8, "var": mock.Mock()}
        app.dup_items = [removed, failed]
        app.dup_groups = [{"group_id": 1, "items": [removed, failed]}]
        app.log = mock.Mock()
        app.btn_dup_delete = mock.Mock()
        app._render_all_dup_groups = mock.Mock()
        app.after = mock.Mock(side_effect=lambda delay, callback: callback())
        with mock.patch.object(dev_cleaner.os.path, "exists", side_effect=[True, False, True]), \
                mock.patch.object(dev_cleaner, "send2trash", side_effect=[None, OSError("locked")]):
            app._bg_delete_duplicates([removed, failed])
        self.assertEqual(app.dup_items, [failed])
        self.assertEqual([group["items"] for group in app.dup_groups], [[failed]])
        failed["var"].set.assert_not_called()

    def test_rerender_reuses_existing_checkbox_selection(self):
        app = dev_cleaner.DevAICleanerApp.__new__(dev_cleaner.DevAICleanerApp)
        selection = mock.Mock()
        selection.get.return_value = False
        item = {"path": "keep.bin", "name": "keep.bin", "size_bytes": 8,
                "mtime": 0, "is_newest": True, "is_oldest": False, "var": selection}
        app.dup_groups = [{"group_id": 1, "size_bytes": 8, "items": [item]}]
        app.dup_items = [item]
        app.dup_scroll = mock.Mock()
        app.dup_scroll.winfo_children.return_value = []
        app.log = mock.Mock()
        app.update_dup_savings_counter = mock.Mock()
        with mock.patch.object(dev_cleaner.ctk, "CTkFrame"), \
                mock.patch.object(dev_cleaner.ctk, "CTkLabel"), \
                mock.patch.object(dev_cleaner.ctk, "CTkButton"), \
                mock.patch.object(dev_cleaner.ctk, "CTkCheckBox") as checkbox, \
                mock.patch.object(dev_cleaner.ctk, "CTkFont"), \
                mock.patch.object(dev_cleaner.tk, "BooleanVar") as variable:
            app._render_all_dup_groups()
        self.assertIs(item["var"], selection)
        self.assertIs(checkbox.call_args.kwargs["variable"], selection)
        variable.assert_not_called()


if __name__ == "__main__":
    unittest.main()
