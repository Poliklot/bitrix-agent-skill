import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_runtime_evidence as runtime
import validate_optimization_evidence as optimization
from evidence_safety import MAX_EVIDENCE_SIZE


class EvidenceSafetyTests(unittest.TestCase):
    def packs(self):
        return [
            (ROOT / "examples/runtime-smoke/blocked-p1", lambda p: runtime.validate_evidence(p, ["P1"])),
            (ROOT / "examples/optimization-evidence/sample-candidate", optimization.validate_evidence),
        ]

    def test_examples_pass(self):
        for source, validate in self.packs():
            self.assertTrue(all(c.ok for c in validate(source)))

    def test_unscanned_and_secret_files_fail_without_echoing_values(self):
        payloads = [b'{"token": "FAKE_SECRET_VALUE"}',
                    b'Authorization: Basic RkFLRV9TRUNSRVQ=',
                    b'https://test:FAKE_SECRET_VALUE@example.test',
                    b'\x00binary', b'\xff', b'a' * (MAX_EVIDENCE_SIZE + 1)]
        for source, validate in self.packs():
            for payload in payloads:
                with self.subTest(pack=source.name, size=len(payload)), tempfile.TemporaryDirectory() as tmp:
                    pack = Path(tmp) / "pack"
                    shutil.copytree(source, pack)
                    (pack / "extra.txt").write_bytes(payload)
                    checks = validate(pack)
                    self.assertTrue(any(not c.ok for c in checks))
                    self.assertNotIn("FAKE_SECRET_VALUE", str(checks))

    def test_linked_evidence_fails(self):
        for source, validate in self.packs():
            with tempfile.TemporaryDirectory() as tmp:
                pack = Path(tmp) / "pack"
                shutil.copytree(source, pack)
                (pack / "linked").symlink_to(source, target_is_directory=True)
                self.assertTrue(any(not c.ok for c in validate(pack)))
