"""Configuration, root resolution, and shared utilities."""

from __future__ import annotations

import datetime as dt
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from aih.constants import SEARCH_DIRS
from typing import cast

# ---------------------------------------------------------------------------
# ROOT resolution
# ---------------------------------------------------------------------------

_SCRIPT_PARENT = Path(__file__).resolve().parents[1]


def _detect_root() -> Path:
    """Resolve the harness root directory.

    Priority:
      1. AI_HARNESS_HOME environment variable
      2. Config file setting (loaded later, can override)
      3. Auto-detect: parent of the aih/ package if it contains INDEX.md
    """
    env = os.environ.get("AI_HARNESS_HOME")
    if env:
        return Path(env).expanduser().resolve()
    # Auto-detect from package location (works when running from the repo)
    if (_SCRIPT_PARENT / "INDEX.md").exists():
        return _SCRIPT_PARENT
    return _SCRIPT_PARENT


ROOT = _detect_root()


def set_root(path: Path) -> None:
    """Override ROOT at runtime (used by tests and config loading)."""
    global ROOT  # noqa: PLW0603
    ROOT = path


# ---------------------------------------------------------------------------
# Config file support
# ---------------------------------------------------------------------------

_CONFIG_SEARCH = [
    Path.home() / ".config" / "ai-harness" / "config.toml",
    Path(".aih.toml"),
]


@dataclass
class Config:
    """User/project configuration with layered defaults."""

    default_target: str = "auto"
    default_mode: str = "auto"
    codex_bin: str = ""
    color: str = "auto"
    deep_threshold: int = 500
    deep_min_terms: int = 2
    router_model: str = "stub"
    harness_home: str = ""
    extra: dict[str, object] = field(default_factory=dict)


def _parse_toml(path: Path) -> dict[str, object]:
    """Parse a TOML file, using tomllib (3.11+) or a minimal fallback.

    Returns a mapping of string keys to primitive objects.
    """
    text = path.read_text()
    try:
        import tomllib  # noqa: PLC0415
        return cast(dict[str, object], tomllib.loads(text))
    except ImportError:
        pass
    try:
        import tomli  # noqa: PLC0415
        return cast(dict[str, object], tomli.loads(text))
    except ImportError:
        pass
    # Minimal key=value fallback (flat TOML only)
    result: dict[str, object] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("["):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            value = value.strip().strip('"').strip("'")
            result[key.strip()] = value
    return result


def load_config(extra_paths: list[Path] | None = None) -> Config:
    """Load configuration from disk with layered overrides."""
    merged: dict[str, object] = {}
    search = list(_CONFIG_SEARCH) + (extra_paths or [])
    for path in search:
        resolved = path.expanduser().resolve()
        if resolved.is_file():
            try:
                data = _parse_toml(resolved)
                # Flatten one level of sections
                for key, value in data.items():
                    if isinstance(value, dict):
                        merged.update(value)
                    else:
                        merged[key] = value
            except Exception:
                pass  # Skip malformed config files silently

    cfg = Config(
        default_target=str(merged.get("target", merged.get("default_target", "auto"))),
        default_mode=str(merged.get("mode", merged.get("default_mode", "auto"))),
        codex_bin=str(merged.get("codex_bin", "")),
        color=str(merged.get("color", "auto")),
        deep_threshold=int(cast(str, merged.get("deep_threshold", 500))),
        deep_min_terms=int(cast(str, merged.get("deep_min_terms", 2))),
# duplicate deep_min_terms line removed
        harness_home=str(merged.get("harness_home", "")),
        extra={k: v for k, v in merged.items() if k not in {
            "target", "default_target", "mode", "default_mode",
            "codex_bin", "color", "deep_threshold", "deep_min_terms", "harness_home",
        }},
    )

    # Apply harness_home from config if set and not overridden by env
    if cfg.harness_home and not os.environ.get("AI_HARNESS_HOME"):
        set_root(Path(cfg.harness_home).expanduser().resolve())

    return cfg


# ---------------------------------------------------------------------------
# Shared utilities
# ---------------------------------------------------------------------------


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def read_version() -> str:
    version_file = ROOT / "VERSION.md"
    if not version_file.exists():
        return "unknown"
    text = version_file.read_text()
    current = re.search(r"Current version:\s*`?([^`\n]+)`?", text)
    if current:
        return current.group(1).strip()
    for line in text.splitlines():
        value = line.strip()
        if value and value.startswith("## "):
            return value.removeprefix("## ").strip()
    return "unknown"


def files() -> list[Path]:
    found: list[Path] = []
    for name in SEARCH_DIRS:
        directory = ROOT / name
        if directory.exists():
            found.extend(sorted(directory.glob("*.md")))
    return sorted(found)


def match_file(query: str) -> Path:
    query_lower = query.lower()
    matches = [p for p in files() if query_lower in p.name.lower() or query_lower in p.stem.lower()]
    if not matches:
        raise SystemExit(f"No harness file matched: {query}")
    return matches[0]
