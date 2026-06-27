"""Unit tests for aih.audit — direct imports, no subprocess."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from aih.audit import redact_request, slugify, unique_dated_dir


class SlugifyTests(unittest.TestCase):
    def test_simple_text(self) -> None:
        self.assertEqual(slugify("fix the bug"), "fix-the-bug")

    def test_truncates_at_70(self) -> None:
        result = slugify("a" * 100)
        self.assertLessEqual(len(result), 70)

    def test_empty_returns_task(self) -> None:
        self.assertEqual(slugify("!!!"), "task")

    def test_strips_special_chars(self) -> None:
        self.assertEqual(slugify("fix (this) [bug]?"), "fix-this-bug")


class RedactRequestTests(unittest.TestCase):
    def test_redacts_api_key(self) -> None:
        self.assertIn("[REDACTED]", redact_request("api_key=super-secret"))

    def test_redacts_sk_token(self) -> None:
        self.assertIn("[REDACTED]", redact_request("use sk-abc123def456ghi"))

    def test_preserves_normal_text(self) -> None:
        self.assertEqual(redact_request("fix the login bug"), "fix the login bug")

    def test_redacts_password(self) -> None:
        self.assertIn("[REDACTED]", redact_request("password=hunter2"))


class UniqueDatedDirTests(unittest.TestCase):
    def test_creates_unique_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            first = unique_dated_dir(parent, "test task")
            first.mkdir()
            second = unique_dated_dir(parent, "test task")
            self.assertNotEqual(first, second)

    def test_first_dir_has_no_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            first = unique_dated_dir(parent, "task")
            self.assertNotRegex(first.name, r"-\d{2}$")


if __name__ == "__main__":
    unittest.main()
