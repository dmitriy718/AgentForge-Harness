"""CLI entry point and command handlers."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from typing import Any, cast
import os
import shutil
import subprocess
import sys
from pathlib import Path

from aih import config as cfg
from aih.audit import (
    append_metadata,
    final_message_summary,
    read_metadata,
    redact_request,
    write_run,
)
from aih.constants import MODES
from aih.display import (
    color,
    print_heading,
    print_item,
    status_text,
    verdict_text,
)
from aih.doctor import (
    build_manifest,
    doctor_payload,
    run_self_tests,
    validation_payload,
)
from aih.health import write_health_snapshot
from aih.prompts import build_prompt, deep_execution_block
from aih.release import create_release
from aih.routing import Overlay, classify_mode, choose_target, infer_risk, is_deep_request, route_intelligently
from aih.shell import install_shell_config


# ---------------------------------------------------------------------------
# Request parsing
# ---------------------------------------------------------------------------


def read_request(args: argparse.Namespace) -> str:
    parts = list(getattr(args, "request", []) or [])
    request = " ".join(parts).strip()

    if getattr(args, "file", None):
        request = Path(args.file).expanduser().read_text().strip()

    if not request and not sys.stdin.isatty():
        request = sys.stdin.read().strip()

    if not request:
        raise SystemExit("Give me a request, or pass --file. Example: aih fix the login bug")

    return request


# ---------------------------------------------------------------------------
# Overlay construction
# ---------------------------------------------------------------------------


def build_overlay(args: argparse.Namespace) -> Overlay:
    request = read_request(args)
    # Use the new intelligent routing to obtain mode, target, risk, deep flag
    result, target = route_intelligently(
        request,
        explicit_mode=args.mode if args.mode != "auto" else None,
        explicit_target=args.target,
    )
    # Construct Overlay for backward-compatible code paths
    overlay = Overlay(
        request=result.request,
        mode=result.mode,
        target=result.target,
        cwd=Path.cwd(),
        risk=result.risk,
    )
    return overlay


def overlay_from_args(args: argparse.Namespace) -> tuple[Overlay, str]:
    overlay = build_overlay(args)
    return overlay, build_prompt(overlay)


def route_payload(overlay: Overlay) -> dict[str, object]:
    mode_spec = MODES[overlay.mode]
    # Deep execution flag is recomputed for consistency
    deep = is_deep_request(overlay.request)
    return {
        "request": redact_request(overlay.request),
        "mode": overlay.mode,
        "mode_title": mode_spec["title"],
        "target": overlay.target,
        "risk": overlay.risk,
        "deep_execution": is_deep_request(overlay.request),
        "workspace": str(overlay.cwd),
        "recommended_route": mode_spec["route"],
    }


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------


def print_completion_summary(overlay: Overlay, run_dir: Path, final_out: Path, exit_code: int) -> None:
    status = "success" if exit_code == 0 else "failed"
    status_value = color(status, "green" if exit_code == 0 else "red", "bold", stream=sys.stderr)
    print("", file=sys.stderr)
    print_heading("AIH run complete", file=sys.stderr)
    print_item("Status", f"{status_value} (exit {exit_code})", file=sys.stderr)
    print_item("Request", redact_request(overlay.request), file=sys.stderr)
    print_item("Mode/target/risk", f"{overlay.mode}/{overlay.target}/{overlay.risk}", file=sys.stderr)
    print_item("Run record", run_dir, file=sys.stderr)
    print_item("Final response", final_out, file=sys.stderr)
    print_item("High-level summary", "", file=sys.stderr)
    for line in final_message_summary(final_out).splitlines():
        print(f"  {line}", file=sys.stderr)


def print_prompt_only_hint(overlay: Overlay) -> None:
    if overlay.target != "codex":
        return

    print("", file=sys.stderr)
    print(color("AIH prompt-only mode: no work was executed.", "yellow", "bold", stream=sys.stderr), file=sys.stderr)
    if is_deep_request(overlay.request):
        print("AIH deep execution would be used if you run this request.", file=sys.stderr)
    print("To execute with Codex, remove `prompt` or use `aih do ...`.", file=sys.stderr)


def print_run_record_hint(overlay: Overlay) -> None:
    if overlay.target != "codex":
        return

    print("", file=sys.stderr)
    print(color("AIH run-record mode: no work was executed.", "yellow", "bold", stream=sys.stderr), file=sys.stderr)
    if is_deep_request(overlay.request):
        print("AIH deep execution plan was saved in the run directory.", file=sys.stderr)
    print("To execute with Codex, use plain `aih ...` or `aih do ...`.", file=sys.stderr)


def print_dry_run_preview(overlay: Overlay, prompt: str) -> None:
    """Print a full dry-run preview of what execution would do."""
    print_heading("AIH dry-run preview", file=sys.stderr)
    print_item("Request", redact_request(overlay.request), file=sys.stderr)
    print_item("Mode", f"{MODES[overlay.mode]['title']} ({overlay.mode})", file=sys.stderr)
    print_item("Target", overlay.target, file=sys.stderr)
    print_item("Risk", overlay.risk, file=sys.stderr)
    print_item("Deep execution", is_deep_request(overlay.request), file=sys.stderr)
    print_item("Workspace", overlay.cwd, file=sys.stderr)
    print_item("Recommended route", MODES[overlay.mode]["route"], file=sys.stderr)
    print("", file=sys.stderr)
    print_heading("Generated prompt", file=sys.stderr)
    print(prompt, file=sys.stderr)


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------


def cmd_route(args: argparse.Namespace) -> None:
    overlay = build_overlay(args)
    payload = route_payload(overlay)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return

    print_heading("AIH route preview")
    print_item("Request", payload["request"])
    print_item("Mode", f"{payload['mode_title']} ({payload['mode']})")
    print_item("Target", payload["target"])
    print_item("Risk", payload["risk"])
    print_item("Deep execution", payload["deep_execution"])
    print_item("Workspace", payload["workspace"])
    print_item("Recommended route", payload["recommended_route"])


def cmd_do(args: argparse.Namespace) -> None:
    overlay, prompt = overlay_from_args(args)

    if overlay.target != "codex":
        print(prompt)
        print(f"\nAIH did not auto-execute because target is {overlay.target}. Use --target codex to execute with Codex.")
        return

    # Dry-run mode: preview and optionally confirm
    if getattr(args, "dry_run", False):
        print_dry_run_preview(overlay, prompt)
        print("", file=sys.stderr)
        print(color("Dry-run complete. No work was executed.", "yellow", "bold", stream=sys.stderr), file=sys.stderr)
        print("Run without --dry-run to execute.", file=sys.stderr)
        return

    codex = os.environ.get("AIH_CODEX_BIN") or shutil.which("codex")
    if not codex:
        print(prompt)
        raise SystemExit("\nAIH could not find the codex CLI, so it printed the strengthened prompt instead.")

    run_dir = write_run(prompt, overlay)
    final_out = run_dir / "codex-final.md"
    command = [
        codex,
        "exec",
        "--cd",
        str(overlay.cwd),
        "--skip-git-repo-check",
        "--sandbox",
        "workspace-write",
        "--output-last-message",
        str(final_out),
        prompt,
    ]
    append_metadata(run_dir, execution="codex exec", final_output=final_out)

    if is_deep_request(overlay.request):
        print(color("AIH deep execution detected.", "cyan", "bold", stream=sys.stderr), file=sys.stderr)
        print(f"AIH execution plan: {run_dir / 'execution-plan.md'}", file=sys.stderr)
    print(f"AIH executing with Codex. Run record: {run_dir}", file=sys.stderr)
    result = subprocess.run(command)
    append_metadata(run_dir, completed=cfg.utc_now().isoformat(timespec="seconds"), exit_code=result.returncode)
    print_completion_summary(overlay, run_dir, final_out, result.returncode)
    raise SystemExit(result.returncode)


def cmd_ask(args: argparse.Namespace) -> None:
    overlay, prompt = overlay_from_args(args)

    if args.out:
        out = Path(args.out).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(prompt)
        print(out)
        print_prompt_only_hint(overlay)
        return

    if args.save:
        run_dir = write_run(prompt, overlay)
        print(run_dir / "prompt.md")
        print_prompt_only_hint(overlay)
        return

    print(prompt)
    print_prompt_only_hint(overlay)


def cmd_run(args: argparse.Namespace) -> None:
    overlay, prompt = overlay_from_args(args)
    run_dir = write_run(prompt, overlay)
    print(run_dir)
    print_run_record_hint(overlay)


def cmd_latest_run(args: argparse.Namespace) -> None:
    run_root = cfg.ROOT / "runs"
    candidates = (path.parent for path in run_root.glob("*/metadata.txt"))
    run_dir = max(candidates, key=lambda path: ((path / "metadata.txt").stat().st_mtime, path.name), default=None)
    if run_dir is None:
        raise SystemExit(f"No AIH run records found under: {run_root}")

    metadata = read_metadata(run_dir / "metadata.txt")
    request_path = run_dir / "request.txt"
    request = request_path.read_text(errors="replace").strip() if request_path.exists() else ""
    payload = {
        "run_dir": str(run_dir),
        "request": request,
        "metadata": metadata,
        "prompt": str(run_dir / "prompt.md") if (run_dir / "prompt.md").exists() else "",
        "final_response": str(run_dir / "codex-final.md") if (run_dir / "codex-final.md").exists() else "",
        "execution_plan": str(run_dir / "execution-plan.md") if (run_dir / "execution-plan.md").exists() else "",
    }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return

    print_heading("AIH latest run")
    print_item("Run record", payload["run_dir"])
    if payload["request"]:
        print_item("Request", payload["request"])
    if isinstance(metadata, dict) and metadata:
        mode = metadata.get("mode", "unknown")
        target = metadata.get("target", "unknown")
        risk = metadata.get("risk", "unknown")
        print_item("Mode/target/risk", f"{mode}/{target}/{risk}")
    if payload["prompt"]:
        print_item("Prompt", payload["prompt"])
    if payload["execution_plan"]:
        print_item("Execution plan", payload["execution_plan"])
    if payload["final_response"]:
        print_item("Final response", payload["final_response"])


def cmd_list(_: argparse.Namespace) -> None:
    for path in cfg.files():
        print(f"{path.relative_to(cfg.ROOT)}")


def cmd_show(args: argparse.Namespace) -> None:
    path = cfg.match_file(args.query)
    print(path.read_text())


def cmd_new_run(args: argparse.Namespace) -> None:
    from aih.audit import unique_run_dir  # noqa: PLC0415

    run_dir = unique_run_dir(args.slug)
    run_dir.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(cfg.ROOT / "templates" / "00-universal-task-brief.md", run_dir / "task-brief.md")
    (run_dir / "evidence.md").write_text("# Evidence\n\n")
    (run_dir / "decisions.md").write_text("# Decisions\n\n")
    (run_dir / "handoff.md").write_text((cfg.ROOT / "templates" / "07-agent-handoff.md").read_text())
    print(run_dir)


def cmd_install_shell(args: argparse.Namespace) -> None:
    path = Path(args.path).expanduser() if args.path else None
    if path:
        changed = install_shell_config(path)
    else:
        changed = install_shell_config()
    status = "installed" if changed else "already installed"
    from aih.constants import SHELL_ENV  # noqa: PLC0415

    display_path = path or SHELL_ENV
    print_heading(f"AIH shell punctuation fix {status}")
    print_item("Path", display_path)
    print_item("Activate now", f"source {display_path}")


def cmd_compile(args: argparse.Namespace) -> None:
    template = cfg.match_file(args.template)
    brief = Path(args.brief).expanduser()
    if not brief.exists():
        raise SystemExit(f"Brief not found: {brief}")
    parts = [
        "# Compiled Harness Prompt",
        f"Generated: {dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')}",
        f"Template: {template.relative_to(cfg.ROOT)}",
        "",
        "## Template",
        template.read_text(),
        "",
        "## Filled Brief",
        brief.read_text(),
        "",
        "## Required Agent Behavior",
        "- Separate facts, assumptions, unknowns, and inferences.",
        "- Do not invent missing evidence.",
        "- State validation steps and rollback.",
        "- Stop before destructive or irreversible changes.",
    ]
    output = "\n".join(parts)
    if args.out:
        out = Path(args.out).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(output)
        print(out)
    else:
        print(output)


def cmd_doctor(args: argparse.Namespace) -> None:
    payload, failed = doctor_payload(strict=args.strict)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        raise SystemExit(1 if failed else 0)

    # Cast for mypy clarity
    payload_dict = cast(dict[str, Any], payload)
    checks = cast(list[dict[str, Any]], payload_dict.get("checks", []))

    print_heading(f"AIH doctor {verdict_text(not failed)}")
    print_item("Root", payload_dict["root"])
    print_item("Version", payload_dict["version"])
    print_item("Strict", payload_dict["strict"])
    print("")
    for check in checks:
        st = status_text(str(check.get("status")))
        print(f"{st:4} {check.get('name')}: {check.get('detail')}")
    raise SystemExit(1 if failed else 0)


def cmd_manifest(args: argparse.Namespace) -> None:
    manifest = build_manifest()
    if args.json:
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return

    manifest_dict = cast(dict[str, Any], manifest)
    print_heading(f"{manifest_dict['name']} {manifest_dict['version']}")
    print_item("Root", manifest_dict["root"])
    print_item("Commands", ", ".join(cast(list[str], manifest_dict.get("commands", []))))
    print_item("Modes", ", ".join(cast(list[str], list(manifest_dict.get("modes", {}).keys()))))


def cmd_validate(args: argparse.Namespace) -> None:
    payload, failed = validation_payload(strict=args.strict)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        payload_dict = cast(dict[str, Any], payload)
        print_heading(f"AIH validation {verdict_text(bool(payload_dict['ok']))}")
        print_item("Root", payload_dict["root"])
        print_item("Version", payload_dict["version"])
        print_item("Strict", payload_dict["strict"])
        print_item("Doctor", status_text("OK" if payload_dict["doctor_ok"] else "FAIL"))
        print_item("Self-tests", f"{status_text('OK' if payload_dict['self_tests_ok'] else 'FAIL')} (exit {payload_dict['self_tests_exit_code']})")
        print_item("Commands", ", ".join(cast(list[str], payload_dict.get("manifest_commands", []))))

    raise SystemExit(1 if failed else 0)


def cmd_release(args: argparse.Namespace) -> None:
    release_dir, failed = create_release(args.name, strict=args.strict)
    print(release_dir)
    if failed:
        raise SystemExit(1)


def cmd_health(_: argparse.Namespace) -> None:
    out = write_health_snapshot()
    print(out)


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aih",
        description="AI Harness action wrapper: execute plain requests through Codex or print stronger prompts for other LLMs.",
        epilog='Shortcut: aih fix the login bug  ==  aih do "fix the login bug"',
    )
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("do", help="Execute a strengthened request with Codex when routed to Codex")
    p.add_argument("request", nargs="*")
    p.add_argument("--file", help="Read the request from a file")
    p.add_argument("--mode", default="auto", choices=["auto", *MODES.keys()])
    p.add_argument("--target", default="auto", choices=["auto", "codex", "claude", "generic"])
    p.add_argument("--dry-run", action="store_true", help="Preview routing and prompt without executing")
    p.set_defaults(func=cmd_do)

    p = sub.add_parser("ask", help="Build a strengthened overlay prompt from a plain request")
    p.add_argument("request", nargs="*")
    p.add_argument("--file", help="Read the request from a file")
    p.add_argument("--mode", default="auto", choices=["auto", *MODES.keys()])
    p.add_argument("--target", default="auto", choices=["auto", "codex", "claude", "generic"])
    p.add_argument("--out", help="Write the prompt to a file")
    p.add_argument("--save", action="store_true", help="Save the prompt in runs/ and print the path")
    p.set_defaults(func=cmd_ask)

    p = sub.add_parser("prompt", help="Alias for ask: print a strengthened prompt without executing")
    p.add_argument("request", nargs="*")
    p.add_argument("--file", help="Read the request from a file")
    p.add_argument("--mode", default="auto", choices=["auto", *MODES.keys()])
    p.add_argument("--target", default="auto", choices=["auto", "codex", "claude", "generic"])
    p.add_argument("--out", help="Write the prompt to a file")
    p.add_argument("--save", action="store_true", help="Save the prompt in runs/ and print the path")
    p.set_defaults(func=cmd_ask)

    p = sub.add_parser("run", help="Create a run directory containing the strengthened prompt")
    p.add_argument("request", nargs="*")
    p.add_argument("--file", help="Read the request from a file")
    p.add_argument("--mode", default="auto", choices=["auto", *MODES.keys()])
    p.add_argument("--target", default="auto", choices=["auto", "codex", "claude", "generic"])
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("latest-run", help="Show the newest AIH run record and key evidence paths")
    p.add_argument("--json", action="store_true", help="Emit machine-readable run information")
    p.set_defaults(func=cmd_latest_run)

    p = sub.add_parser("route", help="Preview mode, target, risk, and deep-execution routing without generating a prompt")
    p.add_argument("request", nargs="*")
    p.add_argument("--file", help="Read the request from a file")
    p.add_argument("--mode", default="auto", choices=["auto", *MODES.keys()])
    p.add_argument("--target", default="auto", choices=["auto", "codex", "claude", "generic"])
    p.add_argument("--json", action="store_true", help="Emit machine-readable routing information")
    p.set_defaults(func=cmd_route)

    p = sub.add_parser("list", help="List deeper harness files")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("show", help="Show a template/playbook/checklist by partial name")
    p.add_argument("query")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("new-run", help="Create a classic run directory")
    p.add_argument("slug")
    p.set_defaults(func=cmd_new_run)

    p = sub.add_parser("install-shell", help="Install zsh punctuation-safe settings for AIH prompts")
    p.add_argument("--path", help="Shell env file to update; defaults to ~/.config/ai-harness/env.sh")
    p.set_defaults(func=cmd_install_shell)

    p = sub.add_parser("compile", help="Compile a classic template and filled brief into one prompt")
    p.add_argument("template")
    p.add_argument("brief")
    p.add_argument("--out")
    p.set_defaults(func=cmd_compile)

    p = sub.add_parser("doctor", help="Validate harness wiring")
    p.add_argument("--json", action="store_true", help="Emit machine-readable diagnostics")
    p.add_argument("--strict", action="store_true", help="Require optional execution dependencies such as codex")
    p.set_defaults(func=cmd_doctor)

    p = sub.add_parser("manifest", help="Describe harness capabilities for automation")
    p.add_argument("--json", action="store_true", help="Emit machine-readable manifest")
    p.set_defaults(func=cmd_manifest)

    p = sub.add_parser("validate", help="Run doctor, self-tests, and manifest generation as one validation gate")
    p.add_argument("--json", action="store_true", help="Emit machine-readable validation results")
    p.add_argument("--strict", action="store_true", help="Require optional execution dependencies such as codex")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("release", help="Create a production readiness release evidence packet")
    p.add_argument("name", help="Release name or purpose")
    p.add_argument("--strict", action="store_true", help="Require optional execution dependencies such as codex")
    p.set_defaults(func=cmd_release)

    p = sub.add_parser("health", help="Write a system health snapshot")
    p.set_defaults(func=cmd_health)

    return parser


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    subcommands = {"do", "ask", "prompt", "run", "latest-run", "route", "list", "show", "new-run", "install-shell", "compile", "doctor", "manifest", "validate", "release", "health", "-h", "--help"}
    if argv and argv[0] not in subcommands:
        argv = ["do", *argv]

    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    args.func(args)
    return 0


def main_entry() -> None:
    """Entry point for pip-installed console_scripts."""
    raise SystemExit(main())


if __name__ == "__main__":
    raise SystemExit(main())
