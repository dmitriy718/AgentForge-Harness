"""Audit trail management  --  run records, redaction, metadata."""

from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

from aih import config as cfg
from aih.constants import SENSITIVE_REQUEST_PATTERNS
from aih.prompts import deep_execution_block
from aih.routing import Overlay


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug[:70] or "task"


def redact_request(value: str) -> str:
    redacted = value
    for pattern in SENSITIVE_REQUEST_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def unique_dated_dir(parent: Path, name: str) -> Path:
    stamp = dt.date.today().isoformat()
    base = parent / f"{stamp}-{slugify(name)}"
    if not base.exists():
        return base

    for index in range(2, 1000):
        candidate = Path(f"{base}-{index:02d}")
        if not candidate.exists():
            return candidate

    raise SystemExit(f"Could not create a unique directory for: {base}")


def unique_run_dir(request: str) -> Path:
    return unique_dated_dir(cfg.ROOT / "runs", request)


def write_run(prompt: str, overlay: Overlay) -> Path:
    run_dir = unique_run_dir(overlay.request)
    deep_block = deep_execution_block(overlay.request)
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "prompt.md").write_text(prompt)
    (run_dir / "request.txt").write_text(redact_request(overlay.request) + "\n")
    if deep_block:
        (run_dir / "execution-plan.md").write_text(deep_block + "\n")
    (run_dir / "metadata.txt").write_text(
        "\n".join(
            [
                f"created={cfg.utc_now().isoformat(timespec='seconds')}",
                f"mode={overlay.mode}",
                f"target={overlay.target}",
                f"risk={overlay.risk}",
                f"workspace={overlay.cwd}",
                f"version={cfg.read_version()}",
                f"deep_execution={bool(deep_block)}",
                "",
            ]
        )
    )
    return run_dir


def append_metadata(run_dir: Path, **values: object) -> None:
    with (run_dir / "metadata.txt").open("a") as handle:
        for key, value in values.items():
            handle.write(f"{key}={value}\n")


def read_metadata(path: Path) -> dict[str, str]:
    metadata: dict[str, str] = {}
    if not path.exists():
        return metadata

    for line in path.read_text(errors="replace").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        metadata[key.strip()] = value.strip()
    return metadata


def final_message_summary(final_out: Path, limit: int = 1200) -> str:
    if not final_out.exists():
        return "Final Codex response was not captured."

    text = final_out.read_text(errors="replace").strip()
    if not text:
        return "Final Codex response was empty."

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    summary = "\n".join(lines[:12])
    if len(summary) > limit:
        summary = summary[: limit - 3].rstrip() + "..."
    return summary
