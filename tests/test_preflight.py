import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import bitrix_runtime_preflight as preflight


class PreflightTests(unittest.TestCase):
    def test_version_formats(self):
        for source in [
            "define('SM_VERSION', '26.150.0');",
            'const SM_VERSION = "26.150.0";',
            '$arModuleVersion = ["VERSION" => "26.150.0"];',
            '$arModuleVersion["VERSION"] = "26.150.0";',
        ]:
            with self.subTest(source=source):
                self.assertEqual(preflight.parse_module_version(source), "26.150.0")
        self.assertEqual(preflight.parse_module_version('"VERSION" => "PRIVATE_VALUE"'), "")

    def test_main_version_file_priority_and_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            install = root / "bitrix/modules/main/install/version.php"
            general = root / "bitrix/modules/main/classes/general/version.php"
            install.parent.mkdir(parents=True)
            install.write_text('"VERSION" => "1.0.0"')
            self.assertEqual(preflight.module_version_file(root, "main"), install)
            general.parent.mkdir(parents=True)
            general.write_text("define('SM_VERSION', '2.0.0');")
            self.assertEqual(preflight.module_version_file(root, "main"), general)
            self.assertEqual(preflight.collect_modules(root, ["main"])[0]["version"], "2.0.0")
