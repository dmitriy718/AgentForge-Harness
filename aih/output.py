"""Output models for AI-Harness.

We use Pydantic for strict validation of routing results and other
structured data emitted by the system.
"""

from __future__ import annotations

from pydantic import BaseModel


class RoutingResult(BaseModel):
    """Data class describing the outcome of routing a request.

    Attributes
    ----------
    request: str
        The original user request.
    mode: str
        The selected AI-Harness mode (implementation, debug, etc.).
    target: str
        The chosen execution target (codex, claude, generic).
    risk: str
        Risk assessment -- ``high``, ``medium`` or ``normal``.
    deep_execution: bool
        Whether the request is considered a deep execution.
    """

    request: str
    mode: str
    target: str
    risk: str
    deep_execution: bool


def format_result(result: RoutingResult) -> str:
    """Return a pretty-printed JSON representation of ``result``.

    Uses ``model_dump_json`` for Pydantic v2 compatibility.
    """
    return result.model_dump_json(indent=2)

