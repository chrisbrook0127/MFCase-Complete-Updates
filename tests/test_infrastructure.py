"""Exercise real infrastructure safety checks, not application functionality."""
import hashlib
import importlib.util
import stat
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile, ZipInfo

SPEC = importlib.util.spec_from_file_location("verify_infrastructure",
    Path(__file__).resolve().parents[1] / "scripts" / "verify_infrastructure.py")
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)

class InfrastructureTests(unittest.TestCase):
    def fixture_tree(self):
        return dict(guard.ORIGINAL, **{p: ("100644", "blob", "a"*40) for p in guard.ADDED})

    def test_correct_repository_and_tree(self):
        guard.verify_repository("https://github.com/" + guard.REPOSITORY, guard.REPOSITORY)
        guard.verify_tree(self.fixture_tree())

    def test_standalone_repository_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "Wrong repository"):
            guard.verify_repository("https://github.com/chrisbrook0127/CaseNumberOCR-Updates")

    def test_wrong_workflow_repository_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "Wrong GitHub repository"):
            guard.verify_repository("https://github.com/" + guard.REPOSITORY, "owner/other")

    def test_modified_original_rejected(self):
        entries = self.fixture_tree()
        entries["installer"] = ("100644", "blob", "b"*40)
        with self.assertRaisesRegex(RuntimeError, "Protected original"):
            guard.verify_tree(entries)

    def test_unapproved_payload_rejected(self):
        entries = self.fixture_tree()
        entries["private.zip"] = ("100644", "blob", "b"*40)
        with self.assertRaisesRegex(RuntimeError, "unexpected tracked"):
            guard.verify_tree(entries)

    def test_missing_or_symlink_infrastructure_rejected(self):
        entries = self.fixture_tree()
        del entries["AGENTS.md"]
        with self.assertRaisesRegex(RuntimeError, "Missing"):
            guard.verify_tree(entries)
        entries = self.fixture_tree()
        entries["AGENTS.md"] = ("120000", "blob", "a"*40)
        with self.assertRaisesRegex(RuntimeError, "Unsafe"):
            guard.verify_tree(entries)

    def archive_check(self, names, expected=None):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "fixture.zip"
            with ZipFile(path, "w") as archive:
                for name in names:
                    archive.writestr(name, b"synthetic")
            # ZIP writers normalize backslashes on Windows; inject the raw member bytes.
            if any(isinstance(name, str) and chr(92) in name for name in names):
                data = path.read_bytes()
                for name in names:
                    if isinstance(name, str) and chr(92) in name:
                        data = data.replace(name.replace(chr(92), "/").encode(), name.encode())
                path.write_bytes(data)
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            return guard.verify_archive(path, digest if expected is None else expected)

    def test_valid_archive(self):
        self.assertEqual(self.archive_check(["app/code.py", "README.md"]), 2)

    def test_wrong_or_unapproved_digest_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "SHA-256 mismatch"):
            self.archive_check(["app.py"], "0"*64)
        with self.assertRaisesRegex(RuntimeError, "approved SHA-256"):
            self.archive_check(["app.py"], "")

    def test_path_traversal_and_windows_absolute_rejected(self):
        for name in ("../outside.py", "C:/outside.py", "app/../outside.py", "app\\outside.py"):
            with self.subTest(name=name), self.assertRaisesRegex(RuntimeError, "Unsafe"):
                self.archive_check([name])

    def test_windows_reserved_names_rejected(self):
        for name in ("CON.txt", "app/NUL", "app/file. ", "app/data:stream"):
            with self.subTest(name=name), self.assertRaisesRegex(RuntimeError, "Unsafe"):
                self.archive_check([name])

    def test_case_collision_and_prefix_conflict_rejected(self):
        for names in (["app.py", "APP.py"], ["app", "app/code.py"], ["app/code.py", "app"]):
            with self.subTest(names=names), self.assertRaisesRegex(RuntimeError, "[Cc]onflict|[Dd]uplicate"):
                self.archive_check(names)

    def test_symlink_rejected(self):
        info = ZipInfo("link.py")
        info.create_system = 3
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        with self.assertRaisesRegex(RuntimeError, "Unsafe"):
            self.archive_check([info])

if __name__ == "__main__":
    unittest.main()
