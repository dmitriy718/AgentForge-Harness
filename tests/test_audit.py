"""Tests for aih.audit — run records, redaction, metadata, file summary."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from aih import config as cfg
from aih.audit import (
    append_metadata,
    final_message_summary,
    read_metadata,
    redact_request,
    slugify,
    unique_dated_dir,
    unique_run_dir,
    write_run,
)
from aih.routing import Overlay


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

    def test_uppercase_lowered(self) -> None:
        self.assertEqual(slugify("Fix THE Bug"), "fix-the-bug")


class RedactRequestTests(unittest.TestCase):
    def test_redacts_api_key(self) -> None:
        self.assertIn("[REDACTED]", redact_request("api_key=super-secret"))

    def test_redacts_sk_token(self) -> None:
        self.assertIn("[REDACTED]", redact_request("use sk-abc123def456ghi"))

    def test_preserves_normal_text(self) -> None:
        self.assertEqual(redact_request("fix the login bug"), "fix the login bug")

    def test_redacts_password(self) -> None:
        self.assertIn("[REDACTED]", redact_request("password=hunter2"))

    def test_redacts_token(self) -> None:
        self.assertIn("[REDACTED]", redact_request("token=abc123def"))

    def test_redacts_secret(self) -> None:
        self.assertIn("[REDACTED]", redact_request("secret: mysecretvalue"))


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


class WriteRunTests(unittest.TestCase):
    def test_creates_run_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old_root = cfg.ROOT
            cfg.set_root(Path(tmp))
            try:
                (Path(tmp) / "runs").mkdir()
                overlay = Overlay(
                    request="fix the login bug",
                    mode="implementation",
                    target="codex",
                    cwd=Path(tmp),
                    risk="normal",
                )
                run_dir = write_run("# test prompt", overlay)
                self.assertTrue(run_dir.exists())
                self.assertTrue((run_dir / "prompt.md").exists())
                self.assertTrue((run_dir / "request.txt").exists())
                self.assertTrue((run_dir / "metadata.txt").exists())
            finally:
                cfg.set_root(old_root)

    def test_request_is_redacted_in_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old_root = cfg.ROOT
            cfg.set_root(Path(tmp))
            try:
                (Path(tmp) / "runs").mkdir()
                overlay = Overlay(
                    request="debug api_key=secret123 failure",
                    mode="debug",
                    target="codex",
                    cwd=Path(tmp),
                    risk="normal",
                )
                run_dir = write_run("# test prompt", overlay)
                request_text = (run_dir / "request.txt").read_text()
                self.assertIn("[REDACTED]", request_text)
                self.assertNotIn("secret123", request_text)
            finally:
                cfg.set_root(old_root)


class MetadataTests(unittest.TestCase):
    def test_append_and_read_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "metadata.txt"
            path.write_text("key1=value1\n")
            append_metadata(Path(tmp), key2="value2")
            data = read_metadata(path)
            self.assertEqual(data["key1"], "value1")
            self.assertEqual(data["key2"], "value2")

    def test_read_nonexistent_returns_empty(self) -> None:
        data = read_metadata(Path("/nonexistent/metadata.txt"))
        self.assertEqual(data, {})


class FinalMessageSummaryTests(unittest.TestCase):
    def test_missing_file(self) -> None:
        result = final_message_summary(Path("/nonexistent/file.md"))
        self.assertIn("not captured", result)

    def test_empty_file(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("")
            f.flush()
            result = final_message_summary(Path(f.name))
        self.assertIn("empty", result)

    def test_normal_file(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("Changed the harness.\nValidation passed.\n")
            f.flush()
            result = final_message_summary(Path(f.name))
        self.assertIn("Changed the harness.", result)

    def test_truncates_long_content(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("\n".join(f"Line {i}" for i in range(100)))
            f.flush()
            result = final_message_summary(Path(f.name), limit=50)
        self.assertLessEqual(len(result), 50)


if __name__ == "__main__":
    unittest.main()
