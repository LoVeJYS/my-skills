from __future__ import annotations

import argparse
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "scan_site_impact.py"
SPEC = importlib.util.spec_from_file_location("scan_site_impact", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load scanner: {SCRIPT_PATH}")
SCANNER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SCANNER
SPEC.loader.exec_module(SCANNER)


class ScanSiteImpactTest(unittest.TestCase):
    def args(self, root: Path, **overrides: object) -> argparse.Namespace:
        values: dict[str, object] = {
            "root": str(root),
            "reference": ["hk"],
            "scope": [],
            "new_site": "mea",
            "output": None,
            "max_matches_per_file": 50,
            "max_files": 200,
            "exclude_dir": [],
            "include_dir": [],
        }
        values.update(overrides)
        return argparse.Namespace(**values)

    def test_redacts_uri_userinfo_and_sensitive_query_values(self) -> None:
        line = (
            'site="hk" database_url="postgres://alice:s3cr3t@db.example.invalid:5432/hk'
            '?sslmode=require&token=abc123" amqp="amqps://bob:mqpass@mq.example.invalid:5671/hk"'
        )

        safe = SCANNER.redact(line)
        endpoints = SCANNER.extract_endpoints(line)

        for secret in ("alice", "s3cr3t", "abc123", "bob", "mqpass"):
            self.assertNotIn(secret, safe)
            self.assertTrue(all(secret not in endpoint for endpoint in endpoints))
        self.assertIn("postgres://REDACTED@db.example.invalid:5432/hk", safe)
        self.assertIn("amqps://REDACTED@mq.example.invalid:5671/hk", safe)
        self.assertTrue(any(endpoint.startswith("postgres://REDACTED@") for endpoint in endpoints))
        self.assertTrue(any(endpoint.startswith("amqps://REDACTED@") for endpoint in endpoints))

    def test_scans_rust_and_toml_but_excludes_default_and_custom_targets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "src").mkdir()
            (root / "config").mkdir()
            (root / "target").mkdir()
            (root / "artifacts" / "cargo-target").mkdir(parents=True)
            (root / "src" / "site.rs").write_text(
                'enum Site { Hk }\nlet site = Site::Hk;\n', encoding="utf-8"
            )
            (root / "config" / "hk.toml").write_text(
                'site = "hk"\ndatabase_url = "postgres://user:pass@db.invalid:5432/hk"\n',
                encoding="utf-8",
            )
            (root / "target" / "generated-hk.rs").write_text("Hk", encoding="utf-8")
            (root / "artifacts" / "cargo-target" / "generated-hk.rs").write_text(
                "Hk", encoding="utf-8"
            )

            report = SCANNER.build_report(
                self.args(root, exclude_dir=["cargo-target"])
            )
            paths = {item["path"] for item in report["files"]}
            serialized = str(report)

            self.assertIn("src/site.rs", paths)
            self.assertIn("config/hk.toml", paths)
            self.assertFalse(any(path.startswith("target/") for path in paths))
            self.assertFalse(any("cargo-target" in path for path in paths))
            self.assertNotIn("postgres://user:pass@", serialized)
            self.assertNotIn("user:pass", serialized)
            self.assertIn("postgres://REDACTED@db.invalid:5432/hk", serialized)

    def test_include_dir_can_override_a_default_exclusion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "build").mkdir()
            (root / "build" / "hk.rs").write_text("Site::Hk", encoding="utf-8")

            excluded = SCANNER.build_report(self.args(root))
            included = SCANNER.build_report(self.args(root, include_dir=["build"]))

            self.assertEqual(0, excluded["matchedFileCount"])
            self.assertEqual(["build/hk.rs"], [item["path"] for item in included["files"]])
            self.assertIn("build", included["explicitlyIncludedDirectories"])

    def test_scope_cannot_escape_repository_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            with self.assertRaisesRegex(ValueError, "escapes repository root"):
                SCANNER.build_report(self.args(root, scope=[".."]))


if __name__ == "__main__":
    unittest.main()
