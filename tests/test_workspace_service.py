import importlib.util
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import ModuleType
import unittest
from unittest.mock import patch


class WorkspaceServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)
        config = ModuleType("config")
        config.WORKSPACES_DIR = self.directory
        source = Path(__file__).resolve().parents[1] / "services/workspace_service.py"
        spec = importlib.util.spec_from_file_location("isolated_workspace_service", source)
        self.service = importlib.util.module_from_spec(spec)
        # Never import the real config: it creates real AppData directories.
        with patch.dict(sys.modules, {"config": config}):
            spec.loader.exec_module(self.service)

    def test_invalid_names_never_write(self) -> None:
        invalid = ["", " ", "../outside", "..\\outside", "C:\\outside", "a/b",
                   "a:b", "a?b", "a*b", 'a"b', "a<b", "a>b", "a|b",
                   "a\x00b", "a\nb", ".", "..", "name.", " name", "name ",
                   "CON", "con.txt", "NUL", "COM1", "LPT9", "x" * 121]
        for name in invalid:
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.service.save_workspace({"name": name})
        self.assertEqual(list(self.directory.iterdir()), [])

    def test_valid_names_keep_existing_filename_mapping(self) -> None:
        for name in ("Python Development", "Caf\u00e9", "Work-2026", "My.Project"):
            with self.subTest(name=name):
                path = self.service.get_workspace_file(name)
                self.assertEqual(path.name, name.lower().replace(" ", "_") + ".json")

    def test_normalized_duplicate_does_not_overwrite(self) -> None:
        self.service.save_workspace({"name": "My Work"})
        path = self.service.get_workspace_file("My Work")
        before = path.read_bytes()
        for name in ("MY WORK", "my_work"):
            with self.subTest(name=name), self.assertRaises(FileExistsError):
                self.service.save_workspace({"name": name})
        self.assertEqual(path.read_bytes(), before)

    def test_invalid_rename_preserves_original(self) -> None:
        self.service.save_workspace({"name": "Original"})
        path = self.service.get_workspace_file("Original")
        before = path.read_bytes()
        with self.assertRaises(ValueError):
            self.service.save_workspace({"name": "../outside"}, "Original")
        self.assertEqual(path.read_bytes(), before)

    def test_invalid_delete_and_original_name_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.service.delete_workspace("../outside")
        with self.assertRaises(ValueError):
            self.service.save_workspace({"name": "Valid"}, "../outside")
        self.assertEqual(list(self.directory.iterdir()), [])

    def test_rename_and_delete(self) -> None:
        self.service.save_workspace({"name": "Original", "order": 1})
        self.service.save_workspace({"name": "Renamed", "order": 2}, "Original")
        self.assertFalse(self.service.get_workspace_file("Original").exists())
        self.assertEqual(self.service.load_workspaces(), [{"name": "Renamed", "order": 2}])
        self.service.delete_workspace("Renamed")
        self.service.delete_workspace("Renamed")
        self.assertEqual(self.service.load_workspaces(), [])


if __name__ == "__main__":
    unittest.main()
