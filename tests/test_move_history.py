import json
import os
import tempfile
import unittest
from unittest import mock

import dev_cleaner


class DirectoryManifestTests(unittest.TestCase):
    def test_missing_root_cannot_verify_as_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(OSError):
                dev_cleaner.directory_manifest(os.path.join(directory, "missing"))

    def test_file_root_cannot_verify_as_empty(self):
        with tempfile.NamedTemporaryFile() as file:
            with self.assertRaises(OSError):
                dev_cleaner.directory_manifest(file.name)

    def test_reparse_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with mock.patch.object(dev_cleaner, "is_junction", return_value=True):
                with self.assertRaises(OSError):
                    dev_cleaner.directory_manifest(directory)


class RecoveryCleanupTests(unittest.TestCase):
    def test_partial_target_can_be_cleaned_using_saved_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            original = os.path.join(directory, "original")
            target = os.path.join(directory, "target")
            os.mkdir(original)
            os.mkdir(target)
            for name in ("first.bin", "second.bin"):
                with open(os.path.join(original, name), "wb") as file:
                    file.write(b"safe data")
            manifest = dev_cleaner.directory_manifest(original)
            with open(os.path.join(target, "second.bin"), "wb") as file:
                file.write(b"safe data")
            dev_cleaner.cleanup_verified_copy(original, target, manifest)
            self.assertFalse(os.path.lexists(target))
            self.assertEqual(dev_cleaner.directory_manifest(original), manifest)

    def test_changed_target_is_preserved_without_partial_deletion(self):
        with tempfile.TemporaryDirectory() as directory:
            original = os.path.join(directory, "original")
            target = os.path.join(directory, "target")
            os.mkdir(original)
            os.mkdir(target)
            with open(os.path.join(original, "app.bin"), "wb") as file:
                file.write(b"safe data")
            with open(os.path.join(target, "new.bin"), "wb") as file:
                file.write(b"unrelated data")
            with self.assertRaises(OSError):
                dev_cleaner.cleanup_verified_copy(original, target,
                                                  dev_cleaner.directory_manifest(original))
            self.assertTrue(os.path.isfile(os.path.join(target, "new.bin")))

    def test_changed_original_blocks_cleanup(self):
        with tempfile.TemporaryDirectory() as directory:
            original = os.path.join(directory, "original")
            target = os.path.join(directory, "target")
            os.mkdir(original)
            os.mkdir(target)
            manifest = dev_cleaner.directory_manifest(original)
            with open(os.path.join(original, "new.bin"), "wb") as file:
                file.write(b"changed")
            with self.assertRaises(OSError):
                dev_cleaner.cleanup_verified_copy(original, target, manifest)
            self.assertTrue(os.path.isdir(target))


class LocalMoveHistoryTests(unittest.TestCase):
    def test_corrupt_local_history_blocks_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "moves.json")
            with open(path, "w", encoding="utf-8") as file:
                file.write("not json")
            with mock.patch.object(dev_cleaner, "MOVES_HISTORY_FILE", path):
                with self.assertRaises((OSError, ValueError)):
                    dev_cleaner.load_moves_history()

    def test_recovery_fields_survive_local_history_load(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "moves.json")
            record = {"name": "Example", "original_path": "C:/Example",
                      "target_path": "D:/Example", "operation_id": "fixture-operation",
                      "phase": "restored_pending_cleanup", "manifest": {"app.bin": "hash"}}
            with open(path, "w", encoding="utf-8") as file:
                json.dump([record], file)
            with mock.patch.object(dev_cleaner, "MOVES_HISTORY_FILE", path), \
                    mock.patch.object(dev_cleaner.os.path, "exists", side_effect=lambda value: value == path):
                loaded = dev_cleaner.load_moves_history()
            for field in ("operation_id", "phase", "manifest"):
                self.assertEqual(loaded[0].get(field), record[field])

    def test_standalone_history_does_not_read_external_winup(self):
        with tempfile.TemporaryDirectory() as directory:
            local = os.path.join(directory, "absent.json")
            external = os.path.join(directory, "external.json")
            with open(external, "w", encoding="utf-8") as file:
                json.dump([{"Original": "C:/Example", "Destination": "D:/Example"}], file)
            with mock.patch.object(dev_cleaner, "MOVES_HISTORY_FILE", local), \
                    mock.patch.object(dev_cleaner, "WINUP_MOVES_FILE", external, create=True):
                self.assertEqual(dev_cleaner.load_moves_history(), [])


if __name__ == "__main__":
    unittest.main()
