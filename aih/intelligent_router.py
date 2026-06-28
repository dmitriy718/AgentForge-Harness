"""Intelligent routing module for AI-Harness.

This module provides a stub implementation that forwards to the legacy
keyword classifier but is structured so that a real LLM call can replace
the body without affecting callers.
"""

from __future__ import annotations

try:
    from pydantic import BaseModel, Field
except ImportError:
    BaseModel = object  # type: ignore
    Field = lambda **kwargs: None  # type: ignore

from aih.config import load_config


class RouterResponse(BaseModel):
    """Explicit contract for the LLM routing decision.
    
    This enforces structured outputs from any model integrated in the future.
    """
    mode: str = Field(..., description="The calculated execution mode (e.g., 'ask', 'do', 'deep')")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Confidence score of the routing decision")
    reasoning: str = Field("", description="Optional explanation for the route selection")

def intelligent_route(request: str) -> str:
    """Determine the routing *mode* for *request*.

    The function first checks ``router_model`` in the configuration. If a
    concrete model is configured, it would call the appropriate LLM API
    (OpenAI, Anthropic, etc.). For now we keep a stub that simply forwards
    to :func:`classify_mode`.
    """
    cfg = load_config()
    model = cfg.router_model
    if model == "stub":
        # Lazy import to avoid circular dependency with routing module
        from aih.routing import classify_mode  # noqa: PLC0415

        return classify_mode(request)
    # Placeholder for future LLM integration
    raise NotImplementedError("LLM routing not implemented yet")

