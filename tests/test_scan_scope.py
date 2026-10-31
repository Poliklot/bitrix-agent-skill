import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import bitrix_runtime_preflight as preflight
import bitrix_static_optimization_audit as audit


class ScanScopeTests(unittest.TestCase):
    def test_symlink_files_and_directories_are_not_scanned(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            root = parent / "project"
            local = root / "local"
            local.mkdir(parents=True)
            external = parent / "external"
            external.mkdir()
            source = external / "template.php"
            source.write_text('IncludeComponent(); cleanAll();')
            (local / "template.php").symlink_to(source)
            (local / "linked").symlink_to(external, target_is_directory=True)
            (local / "cycle").symlink_to(root, target_is_directory=True)
            self.assertEqual(list(audit.iter_files(root)), [])
            self.assertEqual(preflight.collect_routes(root), [])
            module = root / "bitrix/modules/main/install"
            module.mkdir(parents=True)
            (module / "version.php").symlink_to(source)
            self.assertEqual(preflight.collect_modules(root, ["main"])[0]["version"], "")

    def test_module_path_injection_is_rejected(self):
        for value in ["../private", "/tmp/main", "main/../../x", "..", "main\\private"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                preflight.module_version_file(Path("/project"), value)
        self.assertEqual(preflight.module_id("vendor.module"), "vendor.module")
