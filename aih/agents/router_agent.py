"""Router agent implementation.

Uses the ``intelligent_route`` function to obtain a mode and then returns a
``RoutingResult`` containing the full routing decision.
"""

from __future__ import annotations

import os
from typing import Any

from aih.agents.base import Agent, AgentError
from aih.intelligent_router import intelligent_route
from aih.output import RoutingResult


class RouterAgent(Agent):
    """Agent that performs intelligent routing via LLM (stub for now)."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("AIH_AGENT_API_KEY")
        if not self.api_key:
            # Allow operation without key for stub mode
            self.api_key = "stub"

    def run(self, request: str) -> RoutingResult:
        """Run routing for *request* and return a ``RoutingResult``.

        Delegates to :func:`intelligent_route`. If the underlying implementation
        raises ``NotImplementedError`` (real LLM not wired), we raise an
        ``AgentError``.
        """
        try:
            mode = intelligent_route(request)
        except NotImplementedError as exc:
            raise AgentError(str(exc)) from exc
        # Use existing helpers for risk and deep detection
        from aih.routing import infer_risk, is_deep_request, choose_target

        risk = infer_risk(request)
        deep = is_deep_request(request)
        # Target selection uses legacy choose_target for now
        target = choose_target(request, "auto", mode)
        return RoutingResult(
            request=request,
            mode=mode,
            target=target,
            risk=risk,
            deep_execution=deep,
        )
