"""Tests for aih.shell — shell config block generation and installation."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from aih.shell import install_shell_config, shell_config_block
from aih.constants import SHELL_BLOCK_BEGIN, SHELL_BLOCK_END


class ShellConfigBlockTests(unittest.TestCase):
    def test_block_contains_markers(self) -> None:
        block = shell_config_block()
        self.assertIn(SHELL_BLOCK_BEGIN, block)
        self.assertIn(SHELL_BLOCK_END, block)

    def test_block_contains_zsh_options(self) -> None:
        block = shell_config_block()
        self.assertIn("unsetopt nomatch bare_glob_qual", block)

    def test_block_ends_with_newline(self) -> None:
        block = shell_config_block()
        self.assertTrue(block.endswith("\n"))


class InstallShellConfigTests(unittest.TestCase):
    def test_install_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "env.sh"
            result = install_shell_config(path)
            self.assertTrue(result)
            self.assertTrue(path.exists())
            text = path.read_text()
            self.assertIn(SHELL_BLOCK_BEGIN, text)

    def test_install_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "env.sh"
            install_shell_config(path)
            result = install_shell_config(path)
            self.assertFalse(result)  # already installed

    def test_install_appends_to_existing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "env.sh"
            path.write_text("# existing content\n")
            install_shell_config(path)
            text = path.read_text()
            self.assertIn("# existing content", text)
            self.assertIn(SHELL_BLOCK_BEGIN, text)

    def test_install_adds_newline_before_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "env.sh"
            path.write_text("no trailing newline")
            install_shell_config(path)
            text = path.read_text()
            # Should have a newline between existing content and the block
            self.assertIn("no trailing newline\n" + SHELL_BLOCK_BEGIN, text)


if __name__ == "__main__":
    unittest.main()
