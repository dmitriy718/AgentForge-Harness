"""Tests for aih.config — configuration loading and caching."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from aih import config as cfg


class ConfigTests(unittest.TestCase):
    def test_detect_root(self) -> None:
        root = cfg._detect_root()
        self.assertTrue(root.exists())

    def test_detect_root_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["AI_HARNESS_HOME"] = tmp
            try:
                root = cfg._detect_root()
                self.assertEqual(root, Path(tmp).resolve())
            finally:
                del os.environ["AI_HARNESS_HOME"]

    def test_parse_toml_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "test.toml"
            p.write_text('key = "value"\n[section]\nother = 123')
            # Assuming tomllib or tomli is installed, but we can't easily force fallback
            # We just test parse_toml works
            data = cfg._parse_toml(p)
            self.assertIn("key", data)

    def test_load_config_defaults(self) -> None:
        cfg._load_config_cached.cache_clear()
        config = cfg.load_config()
        self.assertEqual(config.default_target, "auto")
        self.assertEqual(config.color, "auto")

    def test_read_version(self) -> None:
        version = cfg.read_version()
        self.assertTrue(isinstance(version, str))
        self.assertNotEqual(version, "unknown")

    def test_read_version_unknown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old_root = cfg.ROOT
            cfg.set_root(Path(tmp))
            try:
                version = cfg.read_version()
                self.assertEqual(version, "unknown")
            finally:
                cfg.set_root(old_root)

    def test_match_file_error(self) -> None:
        with self.assertRaises(SystemExit):
            cfg.match_file("nonexistent_file_12345")


if __name__ == "__main__":
    unittest.main()
