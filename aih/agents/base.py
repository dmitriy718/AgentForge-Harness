'''Base class for autonomous agents used by AI‑Harness.

Agents implement a single ``run`` method that receives a request string and
returns an arbitrary Python object (often a ``RoutingResult`` or similar).
'''\n\nfrom __future__ import annotations\n\nimport abc\nfrom typing import Any\n\n\nclass Agent(abc.ABC):\n    """Abstract interface for all agents.
\n    Sub‑classes must implement :meth:`run`.
    """\n\n    @abc.abstractmethod\n    def run(self, request: str) -> Any:\n        """Process *request* and return a result.
\n        Implementations may raise ``AgentError`` on failure.
        """\n        raise NotImplementedError\n\n\nclass AgentError(RuntimeError):\n    """Exception raised when an agent cannot fulfil a request."""\n
