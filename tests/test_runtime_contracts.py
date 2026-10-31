import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_runtime_evidence as runtime


class RuntimeContractsTests(unittest.TestCase):
    def test_inconsistent_records_are_rejected(self):
        mutations = [
            ("summary.md", lambda s: s + "\n| P1-01 | pass | P1-01-modules.md | |\n"),
            ("summary.md", lambda s: s.replace("P1-01-modules.md", "missing.md")),
            ("summary.md", lambda s: s.replace("P1-01-modules.md", "https://example.test/proof")),
            ("summary.md", lambda s: s.replace("| P1-01 | blocked", "| P1-01 | invalid")),
            ("P1-01-modules.md", lambda s: s.replace("Verdict: `blocked`", "Verdict: `pass`")),
            ("P1-01-modules.md", lambda s: s.replace("ID сценария: P1-01", "ID сценария: P1-02")),
            ("P1-01-modules.md", lambda s: ""),
            ("P1-01-modules.md", lambda s: s.replace("безопасный Bitrix sandbox не доступен; write-mode проверка не запускалась.", "")),
        ]
        for filename, mutate in mutations:
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as tmp:
                pack = Path(tmp) / "pack"
                shutil.copytree(ROOT / "examples/runtime-smoke/blocked-p1", pack)
                path = pack / filename
                path.write_text(mutate(path.read_text()))
                self.assertTrue(any(not c.ok for c in runtime.validate_evidence(pack, ["P1"])))

    def test_pass_requires_evidence_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "record.md"
            row = runtime.ScenarioRow("P1-01", "pass", "record.md")
            path.write_text("Scenario: P1-01\nVerdict: pass\n")
            self.assertFalse(runtime.validate_scenario_file(root, row))
            path.write_text(path.read_text() + "\n## Evidence\nSynthetic check output\n")
            self.assertTrue(runtime.validate_scenario_file(root, row))
