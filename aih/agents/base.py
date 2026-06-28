"""Base class for autonomous agents used by AI‑Harness.

Agents implement a single `run` method that receives a request string and
returns an arbitrary Python object (often a `RoutingResult` or similar).
"""

from __future__ import annotations

import abc
from typing import Any


class Agent(abc.ABC):
    """Abstract interface for all agents.

    Sub‑classes must implement :meth:`run`.
    """

    @abc.abstractmethod
    def run(self, request: str) -> Any:
        """Process *request* and return a result.

        Implementations may raise ``AgentError`` on failure.
        """
        raise NotImplementedError


class AgentError(RuntimeError):
    """Exception raised when an agent cannot fulfil a request."""
