"""Tests for aih.security — sanitization, injection prevention, audit logging."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from aih.security import (
    MAX_REQUEST_LENGTH,
    RequestValidationError,
    _JsonFormatter,
    audit_log,
    sanitize_request,
    validate_api_key,
)


class SanitizeRequestTests(unittest.TestCase):
    def test_normal_request_passes(self) -> None:
        result = sanitize_request("fix the login bug")
        self.assertEqual(result, "fix the login bug")

    def test_strips_whitespace(self) -> None:
        result = sanitize_request("  fix the bug  ")
        self.assertEqual(result, "fix the bug")

    def test_empty_request_rejected(self) -> None:
        with self.assertRaises(RequestValidationError):
            sanitize_request("")

    def test_whitespace_only_rejected(self) -> None:
        with self.assertRaises(RequestValidationError):
            sanitize_request("   ")

    def test_too_long_request_rejected(self) -> None:
        with self.assertRaises(RequestValidationError) as ctx:
            sanitize_request("x" * (MAX_REQUEST_LENGTH + 1))
        self.assertIn("exceeds maximum length", str(ctx.exception))

    def test_backtick_injection_blocked(self) -> None:
        with self.assertRaises(RequestValidationError):
            sanitize_request("fix `rm -rf /` the bug")

    def test_command_substitution_blocked(self) -> None:
        with self.assertRaises(RequestValidationError):
            sanitize_request("fix $(rm -rf /) the bug")

    def test_variable_expansion_blocked(self) -> None:
        with self.assertRaises(RequestValidationError):
            sanitize_request("fix ${HOME} the bug")

    def test_semicolon_rm_blocked(self) -> None:
        with self.assertRaises(RequestValidationError):
            sanitize_request("list files; rm -rf /")

    def test_pipe_to_rm_blocked(self) -> None:
        with self.assertRaises(RequestValidationError):
            sanitize_request("find . | rm -rf")

    def test_raw_device_write_blocked(self) -> None:
        with self.assertRaises(RequestValidationError):
            sanitize_request("echo test > /dev/sda")

    def test_etc_overwrite_blocked(self) -> None:
        with self.assertRaises(RequestValidationError):
            sanitize_request("echo test > /etc/passwd")

    def test_safe_shell_chars_allowed(self) -> None:
        # Normal parens, brackets, quotes should pass
        result = sanitize_request("fix this (with parens) [and brackets]?")
        self.assertIn("parens", result)

    def test_dollar_sign_without_paren_allowed(self) -> None:
        result = sanitize_request("costs $50 to fix")
        self.assertIn("$50", result)


class ValidateApiKeyTests(unittest.TestCase):
    def test_none_returns_false(self) -> None:
        self.assertFalse(validate_api_key(None))

    def test_empty_returns_false(self) -> None:
        self.assertFalse(validate_api_key(""))

    def test_stub_allowed_by_default(self) -> None:
        self.assertTrue(validate_api_key("stub"))

    def test_stub_rejected_when_not_allowed(self) -> None:
        self.assertFalse(validate_api_key("stub", allow_stub=False))

    def test_short_key_rejected(self) -> None:
        self.assertFalse(validate_api_key("abc"))

    def test_key_with_spaces_rejected(self) -> None:
        self.assertFalse(validate_api_key("abc def ghi jkl"))

    def test_valid_key_accepted(self) -> None:
        self.assertTrue(validate_api_key("sk-abc123def456"))


class JsonFormatterTests(unittest.TestCase):
    def test_format_produces_valid_json(self) -> None:
        import logging

        formatter = _JsonFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )
        output = formatter.format(record)
        parsed = json.loads(output)
        self.assertEqual(parsed["message"], "test message")
        self.assertEqual(parsed["level"], "INFO")
        self.assertIn("ts", parsed)

    def test_format_includes_extra_data(self) -> None:
        import logging

        formatter = _JsonFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.WARNING,
            pathname="",
            lineno=0,
            msg="warning msg",
            args=(),
            exc_info=None,
        )
        record.extra_data = {"key": "value"}  # type: ignore[attr-defined]
        output = formatter.format(record)
        parsed = json.loads(output)
        self.assertEqual(parsed["data"]["key"], "value")


class AuditLogTests(unittest.TestCase):
    @mock.patch("aih.security._get_json_logger")
    def test_audit_log_calls_logger(self, mock_logger_fn: mock.MagicMock) -> None:
        mock_logger = mock.MagicMock()
        mock_logger_fn.return_value = mock_logger
        audit_log("test_event", user="dima")
        mock_logger.makeRecord.assert_called_once()
        mock_logger.handle.assert_called_once()


if __name__ == "__main__":
    unittest.main()
