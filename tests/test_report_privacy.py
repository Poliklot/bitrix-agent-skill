import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import bitrix_runtime_preflight as preflight
import bitrix_static_optimization_audit as audit


class ReportPrivacyTests(unittest.TestCase):
    def test_source_literals_never_exported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "local").mkdir()
            (root / "bitrix/modules").mkdir(parents=True)
            (root / "local/template.php").write_text(
                'IncludeComponent("demo", "", ["token" => "FAKE_PRIVATE_VALUE"]);\n'
                'foreach ($rows as $row) { CIBlockElement::GetList(); } // FAKE_PRIVATE_VALUE\n'
            )
            report = preflight.build_report(root, "", ["main"])
            findings, count = audit.build_findings(root, 8)
            self.assertGreater(count, 0)
            self.assertTrue(report["routes"])
            self.assertTrue(findings)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                preflight.print_markdown(report)
            formats = [output.getvalue(), json.dumps(report),
                       audit.render_markdown(root, findings, count),
                       json.dumps([audit.finding_to_json(f) for f in findings])]
            for rendered in formats:
                self.assertNotIn("FAKE_PRIVATE_VALUE", rendered)
            n_plus_one = [f for f in findings if "N+1:" in f.title]
            self.assertTrue(n_plus_one)
            self.assertEqual(n_plus_one[0].kind, "risk")
