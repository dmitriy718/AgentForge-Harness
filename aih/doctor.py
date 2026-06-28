"""Doctor checks, manifest, and validation gate."""

from __future__ import annotations

import shutil
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from aih import config as cfg
from aih.constants import CORE_DIRS, CORE_FILES


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    detail: str
    required: bool = True

    @property
    def status(self) -> str:
        if self.ok:
            return "OK"
        return "FAIL" if self.required else "WARN"


def doctor_checks(strict: bool = False) -> list[Check]:
    checks: list[Check] = [
        Check("root exists", cfg.ROOT.exists(), str(cfg.ROOT)),
        Check("aih executable", (cfg.ROOT / "scripts" / "aih").exists(), str(cfg.ROOT / "scripts" / "aih")),
        Check("system python", shutil.which("python3") is not None, shutil.which("python3") or "missing"),
    ]

    for directory in CORE_DIRS:
        checks.append(Check(f"{directory}/ exists", (cfg.ROOT / directory).is_dir(), directory))

    for filename in CORE_FILES:
        checks.append(Check(f"{filename} exists", (cfg.ROOT / filename).is_file(), filename))

    harness_files = cfg.files()
    stem_counts = Counter(path.stem for path in harness_files)
    duplicate_stems = sorted(stem for stem, count in stem_counts.items() if count > 1)
    checks.append(Check("harness files indexed", len(harness_files) >= 20, f"{len(harness_files)} markdown files"))
    checks.append(Check("no duplicate harness file names", not duplicate_stems, ", ".join(duplicate_stems) or "none"))

    codex_skill = Path.home() / ".codex/skills/dmitriy-ai-harness/SKILL.md"
    checks.append(Check("codex skill installed", codex_skill.exists(), str(codex_skill), required=False))
    checks.append(Check("codex cli available", shutil.which("codex") is not None, shutil.which("codex") or "missing", required=strict))
    checks.append(Check("git available", shutil.which("git") is not None, shutil.which("git") or "missing", required=False))
    checks.append(Check("release records directory", (cfg.ROOT / "runs" / "releases").is_dir(), "runs/releases", required=False))
    return checks


def doctor_payload(strict: bool = False) -> tuple[dict[str, object], bool]:
    checks = doctor_checks(strict=strict)
    failed = any(not check.ok and check.required for check in checks)
    payload = {
        "ok": not failed,
        "strict": strict,
        "root": str(cfg.ROOT),
        "version": cfg.read_version(),
        "generated_at": cfg.utc_now().isoformat(timespec="seconds"),
        "checks": [
            {
                "name": check.name,
                "status": check.status,
                "ok": check.ok,
                "required": check.required,
                "detail": check.detail,
            }
            for check in checks
        ],
    }
    return payload, failed


def build_manifest() -> dict[str, object]:
    from aih.constants import SEARCH_DIRS  # noqa: PLC0415

    return {
        "name": "Dmitriy AI Harness",
        "version": cfg.read_version(),
        "root": str(cfg.ROOT),
        "generated_at": cfg.utc_now().isoformat(timespec="seconds"),
        "commands": sorted({"ask", "compile", "do", "doctor", "health", "install-shell", "latest-run", "list", "manifest", "new-run", "prompt", "release", "route", "run", "show", "validate"}),
        "modes": {mode: {"title": spec["title"], "route": spec["route"]} for mode, spec in __import__("aih.constants", fromlist=["MODES"]).MODES.items()},
        "search_dirs": SEARCH_DIRS,
        "file_counts": {directory: len(list((cfg.ROOT / directory).glob("*.md"))) if (cfg.ROOT / directory).exists() else 0 for directory in SEARCH_DIRS},
    }


def run_self_tests() -> subprocess.CompletedProcess[str]:
    tests_dir = cfg.ROOT / "tests"
    if tests_dir.is_dir():
        command = [sys.executable, "-m", "unittest", "discover", "-s", str(tests_dir), "-v"]
    else:
        command = [sys.executable, "-m", "unittest", "-v"]
    return subprocess.run(command, cwd=cfg.ROOT, text=True, capture_output=True, timeout=120)


def validation_payload(strict: bool = False) -> tuple[dict[str, object], bool]:
    doctor, doctor_failed = doctor_payload(strict=strict)
    tests = run_self_tests()
    manifest = build_manifest()
    failed = doctor_failed or tests.returncode != 0
    payload = {
        "ok": not failed,
        "strict": strict,
        "root": str(cfg.ROOT),
        "version": cfg.read_version(),
        "generated_at": cfg.utc_now().isoformat(timespec="seconds"),
        "doctor_ok": not doctor_failed,
        "self_tests_ok": tests.returncode == 0,
        "self_tests_exit_code": tests.returncode,
        "manifest_commands": manifest["commands"],
        "doctor": doctor,
    }
    return payload, failed
