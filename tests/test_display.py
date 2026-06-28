"""Unit tests for aih.display — direct imports, no subprocess."""

from __future__ import annotations

import io
import os
import unittest
from unittest import mock

from aih.display import color, status_text, use_color, verdict_text


class UseColorTests(unittest.TestCase):
    def test_always_returns_true(self) -> None:
        old = os.environ.get("AIH_COLOR")
        os.environ["AIH_COLOR"] = "always"
        try:
            self.assertTrue(use_color(io.StringIO()))
        finally:
            if old is None:
                os.environ.pop("AIH_COLOR", None)
            else:
                os.environ["AIH_COLOR"] = old

    def test_never_returns_false(self) -> None:
        old = os.environ.get("AIH_COLOR")
        os.environ["AIH_COLOR"] = "never"
        try:
            self.assertFalse(use_color(io.StringIO()))
        finally:
            if old is None:
                os.environ.pop("AIH_COLOR", None)
            else:
                os.environ["AIH_COLOR"] = old

    def test_no_color_env_returns_false(self) -> None:
        old_color = os.environ.get("AIH_COLOR")
        old_nc = os.environ.get("NO_COLOR")
        os.environ["AIH_COLOR"] = "auto"
        os.environ["NO_COLOR"] = "1"
        try:
            self.assertFalse(use_color(io.StringIO()))
        finally:
            if old_color is None:
                os.environ.pop("AIH_COLOR", None)
            else:
                os.environ["AIH_COLOR"] = old_color
            if old_nc is None:
                os.environ.pop("NO_COLOR", None)
            else:
                os.environ["NO_COLOR"] = old_nc


class ColorTests(unittest.TestCase):
    def test_no_color_returns_plain(self) -> None:
        old = os.environ.get("AIH_COLOR")
        os.environ["AIH_COLOR"] = "never"
        try:
            self.assertEqual(color("hello", "bold"), "hello")
        finally:
            if old is None:
                os.environ.pop("AIH_COLOR", None)
            else:
                os.environ["AIH_COLOR"] = old

    def test_with_color_returns_ansi(self) -> None:
        old = os.environ.get("AIH_COLOR")
        os.environ["AIH_COLOR"] = "always"
        try:
            result = color("hello", "bold")
            self.assertIn("\033[", result)
            self.assertIn("hello", result)
        finally:
            if old is None:
                os.environ.pop("AIH_COLOR", None)
            else:
                os.environ["AIH_COLOR"] = old


class StatusTextTests(unittest.TestCase):
    def test_ok_text(self) -> None:
        old = os.environ.get("AIH_COLOR")
        os.environ["AIH_COLOR"] = "never"
        try:
            self.assertEqual(status_text("OK"), "[  OK  ]")
        finally:
            if old is None:
                os.environ.pop("AIH_COLOR", None)
            else:
                os.environ["AIH_COLOR"] = old
        with mock.patch("aih.display.use_color") as mock_use:
            mock_use.return_value = False
            self.assertEqual(status_text("OK"), "[  OK  ]")
            self.assertEqual(status_text("WARN"), "[ WARN ]")
            self.assertEqual(status_text("FAIL"), "[ FAIL ]")

    def test_unknown_status_passes_through(self) -> None:
        self.assertEqual(status_text("UNKNOWN"), "UNKNOWN")


class VerdictTextTests(unittest.TestCase):
    def test_passed(self) -> None:
        old = os.environ.get("AIH_COLOR")
        os.environ["AIH_COLOR"] = "never"
        try:
            self.assertEqual(verdict_text(True), "passed")
            self.assertEqual(verdict_text(False), "failed")
        finally:
            if old is None:
                os.environ.pop("AIH_COLOR", None)
            else:
                os.environ["AIH_COLOR"] = old


if __name__ == "__main__":
    unittest.main()
