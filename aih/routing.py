"""Routing utilities for AI-Harness.

Provides data structures and routing helpers.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

from aih.constants import DEEP_REQUEST_TERMS, MODES
from aih.config import load_config
from aih.output import RoutingResult
from aih.intelligent_router import intelligent_route


@dataclass(frozen=True)
class Overlay:
    """Simple container for routing context used by the CLI.

    Attributes:
        request: The raw request string.
        mode: Determined mode (e.g. ``implementation``).
        target: Execution target (``codex``, ``claude`` or ``generic``).
        cwd: Current working directory.
        risk: Inferred risk level.
    """
    request: str
    mode: str
    target: str
    cwd: Path
    risk: str

# ---------------------------------------------------------------------------
# Legacy keyword-based classification (kept for backward compatibility)
# ---------------------------------------------------------------------------

def classify_mode(request: str, requested_mode: str = "auto") -> str:
    """Determine the mode using the original keyword logic.

    ``requested_mode`` can explicitly set a mode; otherwise ``auto`` triggers
    scoring based on ``MODES``.
    """
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

# ---------------------------------------------------------------------------
# Risk inference (unchanged)
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Target selection (still keyword based but can be extended)
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Deep request detection - configurable thresholds
# ---------------------------------------------------------------------------

def is_deep_request(
    request: str,
    threshold: int | None = None,
    min_terms: int | None = None,
) -> bool:
    """Return ``True`` if the request is considered a deep execution.

    When ``threshold`` or ``min_terms`` are not provided, values from the
    user configuration are used (falling back to 500 / 2).
    """
    if threshold is None or min_terms is None:
        cfg = load_config()
        if threshold is None:
            threshold = cfg.deep_threshold
        if min_terms is None:
            min_terms = cfg.deep_min_terms
    text = request.lower()
    term_hits = sum(1 for term in DEEP_REQUEST_TERMS if term in text)
    return len(request) >= threshold or term_hits >= min_terms

# ---------------------------------------------------------------------------
# High-level routing that returns a validated ``RoutingResult``
# ---------------------------------------------------------------------------

def route_intelligently(
    request: str,
    explicit_mode: str | None = None,
    explicit_target: str = "auto",
) -> Tuple[RoutingResult, str]:
    """Route *request* using the intelligent router.

    Returns a tuple ``(RoutingResult, target)`` where ``target`` is the final
    execution target (codex, claude, generic). ``RoutingResult`` contains the
    mode, risk, and deep-execution flag.
    """
    # Determine mode - use explicit if supplied, otherwise intelligent router
    mode = explicit_mode if explicit_mode else intelligent_route(request)
    # Determine target
    target = choose_target(request, explicit_target, mode)
    # Assess risk and depth
    risk = infer_risk(request)
    deep = is_deep_request(request)
    result = RoutingResult(
        request=request,
        mode=mode,
        target=target,
        risk=risk,
        deep_execution=deep,
    )
    return result, target

__all__ = [
    "classify_mode",
    "choose_target",
    "infer_risk",
    "is_deep_request",
    "intelligent_route",
    "route_intelligently",
]
