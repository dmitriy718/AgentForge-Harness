"""Request classification, routing, and risk assessment."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from aih.constants import DEEP_REQUEST_TERMS, MODES


@dataclass(frozen=True)
class Overlay:
    request: str
    mode: str
    target: str
    cwd: Path
    risk: str


def classify_mode(request: str, requested_mode: str = "auto") -> str:
    if requested_mode != "auto":
        if requested_mode not in MODES:
            raise SystemExit(f"Unknown mode: {requested_mode}")
        return requested_mode

    text = request.lower()
    scores: dict[str, int] = {}
    for mode, spec in MODES.items():
        score = 0
        for keyword in spec["keywords"]:
            if keyword in text:
                score += 2 if " " in keyword else 1
        scores[mode] = score

    best_mode, best_score = max(scores.items(), key=lambda item: item[1])
    return best_mode if best_score else "implementation"


def infer_risk(request: str) -> str:
    text = request.lower()
    high_risk = (
        "production",
        "prod",
        "payment",
        "delete",
        "database",
        "secret",
        "credential",
        "security",
        "auth",
        "customer",
        "medical",
        "legal",
        "financial",
    )
    medium_risk = ("deploy", "migration", "refactor", "install", "upgrade", "permission", "api")
    if any(term in text for term in high_risk):
        return "high"
    if any(term in text for term in medium_risk):
        return "medium"
    return "normal"


def choose_target(request: str, target: str, mode: str) -> str:
    if target != "auto":
        return target
    text = request.lower()

    if mode in {"implementation", "debug"}:
        return "codex"

    if any(term in text for term in ("aih", "repo", "code", "file", "terminal", "test", "codex", "patch", "script", "harness")):
        return "codex"
    if any(term in text for term in ("write", "brainstorm", "summarize", "claude", "draft")):
        return "claude"
    return "generic"


def is_deep_request(request: str, threshold: int = 500, min_terms: int = 2) -> bool:
    text = request.lower()
    term_hits = sum(1 for term in DEEP_REQUEST_TERMS if term in text)
    return len(request) >= threshold or term_hits >= min_terms
