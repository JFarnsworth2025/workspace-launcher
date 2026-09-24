import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from services import json_service


class SaveJsonTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)
        self.path = self.directory / "data.json"
        self.original = b'{"original": true}'
        self.path.write_bytes(self.original)

    def assert_original_preserved(self) -> None:
        self.assertEqual(self.path.read_bytes(), self.original)
        self.assertEqual(list(self.directory.iterdir()), [self.path])

    def test_create_and_replace_unicode(self) -> None:
        data = {"name": "Caf\u00e9", "items": [1, 2]}
        json_service.save_json(self.path, data)
        self.assertEqual(json.loads(self.path.read_text(encoding="utf-8")), data)
        new_path = self.directory / "new.json"
        json_service.save_json(new_path, [])
        self.assertEqual(json.loads(new_path.read_text(encoding="utf-8")), [])
        self.assertEqual(set(self.directory.iterdir()), {self.path, new_path})

    def test_serialization_failure_preserves_original(self) -> None:
        with self.assertRaises(TypeError):
            json_service.save_json(self.path, {"invalid": object()})
        self.assert_original_preserved()

    def test_temporary_file_creation_failure_preserves_original(self) -> None:
        with patch.object(json_service, "NamedTemporaryFile",
                          side_effect=PermissionError("denied")):
            with self.assertRaises(PermissionError):
                json_service.save_json(self.path, {})
        self.assert_original_preserved()

    def test_partial_write_failure_preserves_original(self) -> None:
        factory = json_service.NamedTemporaryFile

        def failing_file(**kwargs):
            file = factory(**kwargs)

            def fail_write(content):
                file.file.write(content[:3])
                raise OSError("disk full")

            file.write = fail_write
            return file

        with patch.object(json_service, "NamedTemporaryFile", side_effect=failing_file):
            with self.assertRaisesRegex(OSError, "disk full"):
                json_service.save_json(self.path, {"new": True})
        self.assert_original_preserved()

    def test_sync_failure_preserves_original(self) -> None:
        with patch.object(json_service.os, "fsync", side_effect=OSError("sync failed")):
            with self.assertRaisesRegex(OSError, "sync failed"):
                json_service.save_json(self.path, {})
        self.assert_original_preserved()

    def test_replacement_failure_preserves_original(self) -> None:
        with patch.object(Path, "replace", side_effect=PermissionError("locked")):
            with self.assertRaisesRegex(PermissionError, "locked"):
                json_service.save_json(self.path, {})
        self.assert_original_preserved()

    def test_cleanup_failure_does_not_hide_save_error(self) -> None:
        with (
            patch.object(Path, "replace", side_effect=OSError("save failed")),
            patch.object(Path, "unlink", side_effect=PermissionError("cleanup failed")),
            self.assertLogs(json_service.logger, level="WARNING"),
        ):
            with self.assertRaisesRegex(OSError, "save failed"):
                json_service.save_json(self.path, {})
        self.assertEqual(self.path.read_bytes(), self.original)


if __name__ == "__main__":
    unittest.main()
