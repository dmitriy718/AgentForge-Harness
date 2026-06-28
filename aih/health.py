"""System health snapshot."""

from __future__ import annotations

import datetime as dt
import subprocess
from pathlib import Path

from aih import config as cfg


def write_health_snapshot() -> tuple[Path, dict[str, object]]:
    run_dir = cfg.ROOT / "runs" / "system-health"
    run_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    out = run_dir / f"health-{stamp}.txt"
    commands = [
        ["uname", "-a"],
        ["uptime"],
        ["free", "-h"],
        ["swapon", "--show"],
        ["df", "-hT"],
        ["systemctl", "--failed", "--no-pager"],
        ["docker", "system", "df"],
    ]
    
    results: dict[str, object] = {
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "metrics": {}
    }
    metrics = {}
    
    with out.open("w") as handle:
        for command in commands:
            cmd_str = " ".join(command)
            handle.write(f"$ {cmd_str}\n")
            try:
                result = subprocess.run(command, text=True, capture_output=True, timeout=60)
                handle.write(result.stdout)
                handle.write(result.stderr)
                handle.write(f"\nexit={result.returncode}\n\n")
                metrics[cmd_str] = {
                    "stdout": result.stdout.strip(),
                    "stderr": result.stderr.strip(),
                    "exit_code": result.returncode
                }
            except Exception as exc:
                handle.write(f"ERROR: {exc}\n\n")
                metrics[cmd_str] = {"error": str(exc)}
    
    results["metrics"] = metrics
    return out, results
