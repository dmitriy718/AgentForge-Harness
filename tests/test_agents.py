"""Tests for aih.agents — base, manager, router_agent."""

from __future__ import annotations

import os
import unittest
from unittest import mock

from aih.agents.base import Agent, AgentError
from aih.agents.manager import get_agent
from aih.agents.router_agent import RouterAgent
from aih.output import RoutingResult


class AgentBaseTests(unittest.TestCase):
    def test_agent_is_abstract(self) -> None:
        with self.assertRaises(TypeError):
            Agent()  # type: ignore[abstract]

    def test_agent_error_is_runtime_error(self) -> None:
        err = AgentError("test")
        self.assertIsInstance(err, RuntimeError)
        self.assertEqual(str(err), "test")


class AgentManagerTests(unittest.TestCase):
    def test_get_router_agent(self) -> None:
        agent = get_agent("router")
        self.assertIsInstance(agent, RouterAgent)

    def test_get_unknown_agent_raises(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            get_agent("nonexistent")
        self.assertIn("Unknown agent", str(ctx.exception))


class RouterAgentTests(unittest.TestCase):
    def test_run_returns_routing_result(self) -> None:
        agent = RouterAgent()
        result = agent.run("fix the harness script")
        self.assertIsInstance(result, RoutingResult)
        self.assertEqual(result.mode, "implementation")
        self.assertEqual(result.target, "codex")

    def test_default_api_key_is_stub(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("AIH_AGENT_API_KEY", None)
            agent = RouterAgent()
            self.assertEqual(agent.api_key, "stub")

    def test_api_key_from_env(self) -> None:
        with mock.patch.dict(os.environ, {"AIH_AGENT_API_KEY": "test-key-123"}):
            agent = RouterAgent()
            self.assertEqual(agent.api_key, "test-key-123")

    def test_explicit_api_key(self) -> None:
        agent = RouterAgent(api_key="explicit-key-456")
        self.assertEqual(agent.api_key, "explicit-key-456")

    def test_debug_request_routes_correctly(self) -> None:
        agent = RouterAgent()
        result = agent.run("debug docker compose login failure")
        self.assertEqual(result.mode, "debug")
        self.assertEqual(result.target, "codex")

    def test_risk_assessment(self) -> None:
        agent = RouterAgent()
        result = agent.run("deploy to production server")
        self.assertEqual(result.risk, "high")


if __name__ == "__main__":
    unittest.main()
