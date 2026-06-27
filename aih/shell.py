"""Shell configuration for zsh punctuation safety."""

from __future__ import annotations

from pathlib import Path

from aih.constants import SHELL_BLOCK_BEGIN, SHELL_BLOCK_END, SHELL_ENV


def shell_config_block() -> str:
    return "\n".join(
        [
            SHELL_BLOCK_BEGIN,
            "# Let unquoted punctuation survive when using AIH from zsh.",
            "# Fixes inputs like: aih prompt fix this (with parens) [and brackets]?",
            'if [ -n "${ZSH_VERSION:-}" ]; then',
            "  unsetopt nomatch bare_glob_qual 2>/dev/null || true",
            "fi",
            SHELL_BLOCK_END,
            "",
        ]
    )


def install_shell_config(path: Path = SHELL_ENV) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text() if path.exists() else ""
    if SHELL_BLOCK_BEGIN in existing and SHELL_BLOCK_END in existing:
        return False

    prefix = "" if not existing or existing.endswith("\n") else "\n"
    path.write_text(existing + prefix + shell_config_block())
    return True
