'''Router agent implementation.

Uses the ``intelligent_route`` function to obtain a mode and then returns a
``RoutingResult`` containing the full routing decision.
'''\n\nfrom __future__ import annotations\n\nimport os\nfrom typing import Any\n\nfrom aih.agents.base import Agent, AgentError\nfrom aih.intelligent_router import intelligent_route\nfrom aih.output import RoutingResult\n\n\nclass RouterAgent(Agent):\n    """Agent that performs intelligent routing via LLM (stub for now)."""
\n    def __init__(self, api_key: str | None = None) -> None:\n        self.api_key = api_key or os.getenv("AIH_AGENT_API_KEY")\n        if not self.api_key:\n            # Allow operation without key for stub mode
            self.api_key = "stub"
\n    def run(self, request: str) -> RoutingResult:\n        """Run routing for *request* and return a ``RoutingResult``.
\n        The method delegates to :func:`intelligent_route`. If the underlying
        implementation raises ``NotImplementedError`` (real LLM not wired), we
        fall back to the stub behaviour.
        """\n        try:\n            mode = intelligent_route(request)\n        except NotImplementedError as exc:\n            raise AgentError(str(exc)) from exc\n        # Use existing helpers for risk and deep detection
        from aih.routing import infer_risk, is_deep_request\n\n        risk = infer_risk(request)\n        deep = is_deep_request(request)\n        # Target selection uses legacy choose_target for now
        from aih.routing import choose_target\n        target = choose_target(request, "auto", mode)\n        return RoutingResult(\n            request=request,\n            mode=mode,\n            target=target,\n            risk=risk,\n            deep_execution=deep,\n        )\n
