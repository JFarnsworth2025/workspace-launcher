import importlib.util
import json
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
        self.assertEqual(self.service.load_workspaces(), [
            {"name": "Renamed", "order": 2, "applications": []}
        ])
        self.service.delete_workspace("Renamed")
        self.service.delete_workspace("Renamed")
        self.assertEqual(self.service.load_workspaces(), [])

    def test_bad_files_do_not_hide_valid_workspaces_or_change_bytes(self) -> None:
        self.service.save_workspace({"name": "Good", "order": 2})
        self.service.save_workspace({"name": "First", "order": 1})
        (self.directory / "broken.json").write_bytes(b'{broken')
        (self.directory / "encoding.json").write_bytes(b'\xff')
        (self.directory / "shape.json").write_text('[]', encoding="utf-8")
        before = {p.name: p.read_bytes() for p in self.directory.iterdir()}
        errors = []
        loaded = self.service.load_workspaces(errors=errors)
        self.assertEqual([w["name"] for w in loaded], ["First", "Good"])
        self.assertEqual(len(errors), 3)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.directory.iterdir()})

    def test_invalid_workspace_fields_are_reported(self) -> None:
        invalid = [
            {"name": "../outside"},
            {"name": "Other"},
            {"name": "Test", "order": "first"},
            {"name": "Test", "order": True},
            {"name": "Test", "order": 1000},
            {"name": "Test", "applications": {}},
            {"name": "Test", "applications": [None]},
            {"name": "Test", "applications": [{"name": "App", "path": ""}]},
            {"name": "Test", "applications": [
                {"name": "App", "path": "app.exe", "arguments": "--flag"}
            ]},
        ]
        for record in invalid:
            with self.subTest(record=record):
                (self.directory / "test.json").write_text(json.dumps(record), encoding="utf-8")
                errors = []
                self.assertEqual(self.service.load_workspaces(errors=errors), [])
                self.assertEqual(len(errors), 1)

    def test_missing_optional_fields_are_normalized_in_memory_only(self) -> None:
        self.service.save_workspace({"name": "Legacy"})
        path = self.directory / "legacy.json"
        before = path.read_bytes()
        self.assertEqual(self.service.load_workspaces(), [
            {"name": "Legacy", "order": 1, "applications": []}
        ])
        self.assertEqual(path.read_bytes(), before)

    def test_unreadable_file_does_not_hide_other_files(self) -> None:
        self.service.save_workspace({"name": "Good"})
        self.service.save_workspace({"name": "Locked"})
        original_open = Path.open

        def open_file(path, *args, **kwargs):
            if path.name == "locked.json":
                raise PermissionError("Access denied")
            return original_open(path, *args, **kwargs)

        errors = []
        with patch.object(Path, "open", open_file):
            loaded = self.service.load_workspaces(errors=errors)
        self.assertEqual([w["name"] for w in loaded], ["Good"])
        self.assertIn("locked.json", errors[0])

    def test_directory_error_is_reported(self) -> None:
        errors = []
        with patch.object(Path, "iterdir", side_effect=PermissionError("denied")):
            self.assertEqual(self.service.load_workspaces(errors=errors), [])
        self.assertIn("directory", errors[0])

    def test_repaired_file_loads_on_retry(self) -> None:
        path = self.directory / "fixed.json"
        path.write_text('{broken', encoding="utf-8")
        errors = []
        self.assertEqual(self.service.load_workspaces(errors=errors), [])
        self.assertTrue(errors)
        path.write_text('{"name": "Fixed"}', encoding="utf-8")
        errors = []
        self.assertEqual(self.service.load_workspaces(errors=errors)[0]["name"], "Fixed")
        self.assertEqual(errors, [])

    def test_errors_are_not_silently_ignored_without_error_list(self) -> None:
        (self.directory / "broken.json").write_text('{broken', encoding="utf-8")
        with self.assertRaises(ValueError):
            self.service.load_workspaces()


if __name__ == "__main__":
    unittest.main()
