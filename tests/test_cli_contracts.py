import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CLIContractsTests(unittest.TestCase):
    def run_script(self, name, *args):
        return subprocess.run([sys.executable, str(ROOT / "scripts" / name), *map(str, args)],
                              text=True, capture_output=True, check=False)

    def test_missing_root_is_honestly_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_script("bitrix_runtime_preflight.py", "--public-root", Path(tmp) / "missing", "--json")
            self.assertEqual(result.returncode, 0)
            report = json.loads(result.stdout)
            self.assertEqual(report["status"], "blocked")
            self.assertEqual(report["runtime_status"], "not_checked")

    def test_invalid_cli_arguments_fail(self):
        cases = [
            ("bitrix_runtime_preflight.py", "--module", "../outside"),
            ("init_runtime_evidence.py", "--all", "--package", "P1"),
            ("init_runtime_evidence.py", "--date", "not-a-date"),
            ("init_optimization_evidence.py", "--static-report", "summary.md"),
            ("bitrix_static_optimization_audit.py", "--max-evidence", "0"),
        ]
        for name, *args in cases:
            with self.subTest(name=name):
                result = self.run_script(name, *args)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("Traceback", result.stderr)

    def test_unfilled_runtime_pack_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "pack"
            created = self.run_script("init_runtime_evidence.py", "--output", root)
            self.assertEqual(created.returncode, 0, created.stderr)
            checked = self.run_script("validate_runtime_evidence.py", root, "--package", "P1")
            self.assertEqual(checked.returncode, 1)
