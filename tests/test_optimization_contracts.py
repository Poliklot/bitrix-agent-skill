import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_optimization_evidence as optimization
import init_optimization_evidence as initializer


class OptimizationContractsTests(unittest.TestCase):
    def test_invalid_records_are_rejected(self):
        mutations = [
            ("summary.md", lambda s: s + "\n| OPT-001 | P1 | component-cache | candidate | OPT-001-finding.md | |\n"),
            ("summary.md", lambda s: s.replace("OPT-001-finding.md", "https://example.test/proof")),
            ("summary.md", lambda s: s.replace("OPT-001-finding.md", "../outside.md")),
            ("OPT-001-finding.md", lambda s: s.replace("- Verdict: candidate", "- Verdict: fixed")),
            ("OPT-001-finding.md", lambda s: s.replace("- Priority: P1", "- Priority: P3")),
            ("OPT-001-finding.md", lambda s: s.replace("- ID: OPT-001", "- ID: OPT-002")),
        ]
        for filename, mutate in mutations:
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as tmp:
                pack = Path(tmp) / "pack"
                shutil.copytree(ROOT / "examples/optimization-evidence/sample-candidate", pack)
                path = pack / filename
                path.write_text(mutate(path.read_text()))
                self.assertTrue(any(not c.ok for c in optimization.validate_evidence(pack)))

    def test_generated_priorities_match_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            initializer.init_evidence(root, 3, "2026-11-01", "test", "static-audit.md", False)
            self.assertTrue(all(c.ok for c in optimization.validate_evidence(root)))

    def test_fixed_requires_separate_local_proof(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            initializer.init_evidence(root, 1, "2026-11-01", "test", "static-audit.md", False)
            for name in ["summary.md", "OPT-001-finding.md"]:
                path = root / name
                path.write_text(path.read_text().replace("candidate", "fixed"))
            self.assertTrue(any(not c.ok for c in optimization.validate_evidence(root)))
            path = root / "OPT-001-finding.md"
            path.write_text(path.read_text().replace("- Runtime evidence:", "- Runtime evidence: proof.txt").replace("- Status: pending / pass / fail / blocked.", "- Status: pass"))
            (root / "proof.txt").write_text("Synthetic evidence fixture; not a real runtime measurement.")
            self.assertTrue(all(c.ok for c in optimization.validate_evidence(root)))
