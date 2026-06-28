"""Input sanitization and security utilities for AI-Harness.

Provides request validation, shell injection prevention, and
structured logging for audit trails.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Structured JSON logger
# ---------------------------------------------------------------------------

_LOG_DIR = Path.home() / ".config" / "ai-harness" / "logs"


def _get_json_logger(name: str = "aih") -> logging.Logger:
    """Return a logger that writes JSON-L to the AIH log directory."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        _LOG_DIR.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(_LOG_DIR / "audit.jsonl")
        handler.setFormatter(_JsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


class _JsonFormatter(logging.Formatter):
    """Emit log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "level": record.levelname,
            "module": record.module,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra_data"):
            entry["data"] = record.extra_data
        return json.dumps(entry, default=str)


def audit_log(message: str, **data: Any) -> None:
    """Write an audit log entry.

    Parameters
    ----------
    message:
        Human-readable description of the event.
    **data:
        Arbitrary key-value pairs attached to the log record.
    """
    logger = _get_json_logger()
    record = logger.makeRecord(
        name=logger.name,
        level=logging.INFO,
        fn="",
        lno=0,
        msg=message,
        args=(),
        exc_info=None,
    )
    record.extra_data = data
    logger.handle(record)


# ---------------------------------------------------------------------------
# Request sanitization
# ---------------------------------------------------------------------------

# Patterns considered dangerous in shell contexts
_SHELL_INJECTION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"[`]"),                          # backtick execution
    re.compile(r"\$\("),                          # command substitution
    re.compile(r"\$\{"),                          # variable expansion
    re.compile(r";\s*(rm|dd|mkfs|chmod|chown)"),  # destructive commands after semicolons
    re.compile(r"\|\s*(rm|dd|mkfs)"),             # pipe to destructive commands
    re.compile(r">\s*/dev/sd"),                   # write to raw block devices
    re.compile(r">\s*/etc/"),                     # overwrite system config
    re.compile(r"(&&|\|\|)\s*(rm|dd|mkfs|chmod)"),# chained destructive commands
    re.compile(r"&\s*$"),                         # background execution
)

# Maximum allowed request length
MAX_REQUEST_LENGTH = 50_000


class RequestValidationError(ValueError):
    """Raised when a request fails security validation."""


def sanitize_request(request: str) -> str:
    """Validate and sanitize a CLI request string.

    Raises :class:`RequestValidationError` if the request contains
    dangerous patterns or exceeds the maximum allowed length.

    Returns the original request (stripped) if it passes all checks.
    """
    stripped = request.strip()

    # Length check
    if len(stripped) > MAX_REQUEST_LENGTH:
        raise RequestValidationError(
            f"Request exceeds maximum length ({len(stripped)} > {MAX_REQUEST_LENGTH})"
        )

    # Empty check
    if not stripped:
        raise RequestValidationError("Request is empty")

    # Shell injection check
    for pattern in _SHELL_INJECTION_PATTERNS:
        match = pattern.search(stripped)
        if match:
            audit_log(
                "shell_injection_blocked",
                pattern=pattern.pattern,
                matched=match.group(),
                request_prefix=stripped[:100],
            )
            raise RequestValidationError(
                f"Request contains potentially dangerous pattern: {match.group()!r}"
            )

    return stripped


def validate_api_key(key: str | None, *, allow_stub: bool = True) -> bool:
    """Check whether an API key is present and structurally valid.

    Parameters
    ----------
    key:
        The API key string (or ``None``).
    allow_stub:
        If ``True``, the literal ``"stub"`` is accepted as valid.
    """
    if key is None or key == "":
        return False
    if allow_stub and key == "stub":
        return True
    # Basic structural validation: at least 8 chars, no whitespace
    if len(key) < 8 or " " in key:
        return False
    return True
