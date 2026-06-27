'''Agent manager – simple registry for AI‑Harness agents.

Provides :func:`get_agent(name)` which returns an instantiated Agent.
'''\n\nfrom __future__ import annotations\n\nfrom typing import Dict\n\nfrom .base import Agent
from .router_agent import RouterAgent\n\n__all__ = ["get_agent"]\n\n# Registry mapping names to Agent classes
_AGENT_REGISTRY: Dict[str, type[Agent]] = {\n    "router": RouterAgent,\n}\n\n\ndef get_agent(name: str) -> Agent:\n    """Return an instance of the named agent.
\n    ``name`` must be a key in :data:`_AGENT_REGISTRY`. ``AIH_AGENT_API_KEY``
    environment variable is passed to the agent constructor when applicable.
    """\n    try:\n        agent_cls = _AGENT_REGISTRY[name]\n    except KeyError as exc:\n        raise ValueError(f"Unknown agent: {name}") from exc\n    return agent_cls()  # type: ignore[arg-type]  # constructors accept no args in stub
