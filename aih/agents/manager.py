"""Agent manager - simple registry for AI-Harness agents.

Provides :func:`get_agent(name)` which returns an instantiated ``Agent``.
"""

from __future__ import annotations

from typing import Dict, Type

from .base import Agent
from .router_agent import RouterAgent

__all__ = ["get_agent"]

# Registry mapping names to Agent classes
_AGENT_REGISTRY: Dict[str, Type[Agent]] = {
    "router": RouterAgent,
}


def get_agent(name: str) -> Agent:
    """Return an instance of the named agent.

    ``name`` must be a key in :data:`_AGENT_REGISTRY`. The ``AIH_AGENT_API_KEY``
    environment variable is passed to the agent constructor when applicable.
    """
    try:
        agent_cls = _AGENT_REGISTRY[name]
    except KeyError as exc:
        raise ValueError(f"Unknown agent: {name}") from exc
    return agent_cls()
