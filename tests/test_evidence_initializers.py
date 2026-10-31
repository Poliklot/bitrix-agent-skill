import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import init_runtime_evidence as runtime
import init_optimization_evidence as optimization


class InitializerTests(unittest.TestCase):
    def test_collisions_do_not_partially_write_packs(self):
        cases = [
            ("P1-08-cache-pass.md", lambda p: runtime.init_evidence("P1", p, False)),
            ("00-preflight.md", lambda p: runtime.init_evidence("P1", p, False)),
            ("p4-marketing-automation", lambda p: runtime.init_all(p, False)),
            ("p4-marketing-automation/P4-08-pull-realtime.md", lambda p: runtime.init_all(p, False)),
            ("OPT-003-finding.md", lambda p: optimization.init_evidence(p, 3, "2026-11-01", "", "static-audit.md", False)),
        ]
        for name, initialize in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                sentinel = root / name
                sentinel.parent.mkdir(parents=True, exist_ok=True)
                sentinel.write_text("KEEP")
                with self.assertRaises((FileExistsError, ValueError)):
                    initialize(root)
                self.assertEqual(sentinel.read_text(), "KEEP")
                self.assertEqual([p for p in root.rglob("*") if p.is_file()], [sentinel])

    def test_force_does_not_follow_symlinks_or_overwrite_static_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "pack"
            root.mkdir()
            outside = Path(tmp) / "outside.md"
            outside.write_text("KEEP")
            (root / "summary.md").symlink_to(outside)
            with self.assertRaises(ValueError):
                runtime.init_evidence("P1", root, True)
            self.assertEqual(outside.read_text(), "KEEP")
            (root / "summary.md").unlink()
            (root / "static-audit.md").write_text("REAL REPORT")
            optimization.init_evidence(root, 1, "2026-11-01", "", "static-audit.md", True)
            self.assertEqual((root / "static-audit.md").read_text(), "REAL REPORT")

    def test_invalid_static_names_write_nothing(self):
        for name in ["", ".", "..", "../outside", "summary.md", "README.md", "OPT-001-finding.md", ".evidence-init.lock"]:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / "pack"
                with self.assertRaises(ValueError):
                    optimization.init_evidence(root, 1, "2026-11-01", "", name, True)
                self.assertFalse(root.exists())

    def test_lock_prevents_concurrent_writers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lock = root / ".evidence-init.lock"
            lock.write_text("other writer")
            with self.assertRaises(FileExistsError):
                runtime.init_evidence("P1", root, True)
            self.assertEqual(lock.read_text(), "other writer")
            self.assertFalse((root / "summary.md").exists())
