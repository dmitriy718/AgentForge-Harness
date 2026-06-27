"""Terminal display and color utilities."""

from __future__ import annotations

import os
import sys
from typing import TextIO

from aih.constants import ANSI


def use_color(stream: TextIO = sys.stdout) -> bool:
    setting = os.environ.get("AIH_COLOR", "auto").lower()
    if setting in {"always", "1", "true", "yes"}:
        return True
    if setting in {"never", "0", "false", "no"} or os.environ.get("NO_COLOR"):
        return False
    return hasattr(stream, "isatty") and stream.isatty()


def color(text: object, *styles: str, stream: TextIO = sys.stdout) -> str:
    value = str(text)
    if not use_color(stream):
        return value
    codes = [ANSI[style] for style in styles if style in ANSI]
    if not codes:
        return value
    return f"\033[{';'.join(codes)}m{value}\033[0m"


def status_text(status: str, stream: TextIO = sys.stdout) -> str:
    style = {"OK": "green", "WARN": "yellow", "FAIL": "red"}.get(status)
    return color(status, style, "bold", stream=stream) if style else status


def verdict_text(ok: bool, stream: TextIO = sys.stdout) -> str:
    return color("passed", "green", "bold", stream=stream) if ok else color("failed", "red", "bold", stream=stream)


def print_heading(title: str, *, file: TextIO = sys.stdout) -> None:
    print(color(title, "cyan", "bold", stream=file), file=file)


def print_item(label: str, value: object, *, file: TextIO = sys.stdout) -> None:
    print(f"- {color(label + ':', 'bold', stream=file)} {value}", file=file)
