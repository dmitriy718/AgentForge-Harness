"""Agent manager - simple registry for AI-Harness agents.

Provides :func:`get_agent(name)` which returns an instantiated ``Agent``.
"""

from __future__ import annotations

from typing import Dict, Type

from .base import Agent
from .router_agent import RouterAgent

__all__ = ["get_agent"]

import sys
if sys.version_info >= (3, 10):
    from importlib.metadata import entry_points
else:
    from importlib_metadata import entry_points  # type: ignore[no-redef]

# Registry mapping names to Agent classes
_AGENT_REGISTRY: Dict[str, Type[Agent]] = {
    "router": RouterAgent,
}

# Discover third-party agents via entry points
# Usage in pyproject.toml:
# [project.entry-points."aih.agents"]
# custom = "my_package.module:CustomAgent"
for ep in entry_points(group="aih.agents"):
    try:
        _AGENT_REGISTRY[ep.name] = ep.load()
    except Exception:
        pass  # Silently skip failed imports for robust discovery


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
