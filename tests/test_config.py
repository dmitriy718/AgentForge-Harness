"""Unit tests for aih.config — direct imports, no subprocess."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from aih.config import Config, load_config, _parse_toml


class ParseTomlTests(unittest.TestCase):
    def test_simple_key_value(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write('target = "claude"\ncolor = "always"\n')
            f.flush()
            result = _parse_toml(Path(f.name))
        self.assertEqual(result["target"], "claude")
        self.assertEqual(result["color"], "always")

    def test_ignores_comments_and_sections(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write('# comment\n[defaults]\ntarget = "codex"\n')
            f.flush()
            result = _parse_toml(Path(f.name))
        # tomllib puts section keys into a nested dict; fallback captures flat
        if "defaults" in result and isinstance(result["defaults"], dict):
            self.assertEqual(result["defaults"]["target"], "codex")
        else:
            self.assertEqual(result["target"], "codex")


class ConfigDefaultsTests(unittest.TestCase):
    def test_default_config(self) -> None:
        cfg = Config()
        self.assertEqual(cfg.default_target, "auto")
        self.assertEqual(cfg.default_mode, "auto")
        self.assertEqual(cfg.color, "auto")
        self.assertEqual(cfg.deep_threshold, 500)
        self.assertEqual(cfg.deep_min_terms, 2)

    def test_load_config_returns_config(self) -> None:
        # Even with no config files, should return defaults
        cfg = load_config(extra_paths=[])
        self.assertIsInstance(cfg, Config)

    def test_load_config_from_file(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write('target = "claude"\ncolor = "never"\ndeep_threshold = 300\n')
            f.flush()
            cfg = load_config(extra_paths=[Path(f.name)])
        self.assertEqual(cfg.default_target, "claude")
        self.assertEqual(cfg.color, "never")
        self.assertEqual(cfg.deep_threshold, 300)


if __name__ == "__main__":
    unittest.main()
