"""Release packet generation."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any, cast

from aih import config as cfg
from aih.audit import unique_dated_dir
from aih.constants import RELEASE_GATES
from aih.doctor import build_manifest, doctor_payload, run_self_tests
from aih.prompts import build_prompt
from aih.routing import Overlay


def release_validation_markdown(name: str, strict: bool, doctor_ok: bool, tests: subprocess.CompletedProcess[str]) -> str:
    gate_lines = "\n".join(f"- [x] {gate}" for gate in RELEASE_GATES)
    return "\n".join(
        [
            f"# Release Validation: {name}",
            "",
            f"- Created: {cfg.utc_now().isoformat(timespec='seconds')}",
            f"- Version: {cfg.read_version()}",
            f"- Strict doctor: {strict}",
            f"- Doctor passed: {doctor_ok}",
            f"- Self-tests passed: {tests.returncode == 0}",
            "",
            "## Production Gates",
            gate_lines,
            "",
            "## Commands",
            "- `aih doctor --json`",
            "- `python3 -m unittest discover -s tests -v`",
            "- `aih manifest --json`",
            "",
            "## Failure Handling",
            "If any required doctor check or self-test fails, do not ship the release. Fix the failed check, rerun `aih release`, and use the newest release packet as evidence.",
            "",
            "## Rollback",
            "Keep the previous release packet under `runs/releases/`. Revert to the previous `scripts/aih` and documentation state, then rerun `aih doctor` and the self-tests before using the harness for production work.",
            "",
        ]
    )


def create_release(name: str, strict: bool = False) -> tuple[Path, bool]:
    release_root = cfg.ROOT / "runs" / "releases"
    release_dir = unique_dated_dir(release_root, name)
    release_dir.mkdir(parents=True, exist_ok=False)

    doctor, doctor_failed = doctor_payload(strict=strict)
    manifest = build_manifest()
    tests = run_self_tests()

    (release_dir / "doctor.json").write_text(json.dumps(doctor, indent=2, sort_keys=True) + "\n")
    (release_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    (release_dir / "self-test.log").write_text(tests.stdout + tests.stderr)
    (release_dir / "validation.md").write_text(release_validation_markdown(name, strict, not doctor_failed, tests))
    (release_dir / "known-limitations.md").write_text(
        "\n".join(
            [
                "# Known Limitations",
                "",
                "- `aih` depends on the Codex CLI for automatic execution; without it, prompt generation still works.",
                "- `aih health` records local system diagnostics and may include machine-specific package, disk, or service names.",
                "- Secret-like values are redacted from `request.txt`, but generated prompts retain the original request so execution context is preserved.",
                "",
            ]
        )
    )
    (release_dir / "support-note.md").write_text(
        "\n".join(
            [
                "# Support Note",
                "",
                "Start with `aih doctor --strict` when diagnosing harness failures.",
                "Use `aih manifest --json` to confirm the available command surface.",
                "For failed Codex executions, inspect the run directory printed in the completion summary, especially `prompt.md`, `metadata.txt`, and `codex-final.md`.",
                "",
            ]
        )
    )
    example = build_prompt(
        Overlay(
            request="fix the failing checkout tests and keep changes minimal",
            mode="implementation",
            target="codex",
            cwd=cfg.ROOT,
            risk="normal",
        )
    )
    (release_dir / "example-prompt.md").write_text(example)

    failed = doctor_failed or tests.returncode != 0
    return release_dir, failed
