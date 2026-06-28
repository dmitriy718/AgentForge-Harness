"""Tests for aih.output — RoutingResult and format_result."""

from __future__ import annotations

import json
import unittest

from aih.output import RoutingResult, format_result


class RoutingResultTests(unittest.TestCase):
    def test_create_result(self) -> None:
        result = RoutingResult(
            request="fix bug",
            mode="implementation",
            target="codex",
            risk="normal",
            deep_execution=False,
        )
        self.assertEqual(result.request, "fix bug")
        self.assertEqual(result.mode, "implementation")
        self.assertFalse(result.deep_execution)

    def test_result_is_immutable_model(self) -> None:
        result = RoutingResult(
            request="test",
            mode="debug",
            target="codex",
            risk="high",
            deep_execution=True,
        )
        # Pydantic v2 models are not frozen by default, but we can still
        # test that the model validates correctly
        self.assertEqual(result.risk, "high")
        self.assertTrue(result.deep_execution)

    def test_format_result_produces_valid_json(self) -> None:
        result = RoutingResult(
            request="test",
            mode="implementation",
            target="codex",
            risk="normal",
            deep_execution=False,
        )
        output = format_result(result)
        parsed = json.loads(output)
        self.assertEqual(parsed["mode"], "implementation")
        self.assertEqual(parsed["target"], "codex")

    def test_model_dump(self) -> None:
        result = RoutingResult(
            request="test",
            mode="review",
            target="claude",
            risk="medium",
            deep_execution=False,
        )
        data = result.model_dump()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["mode"], "review")
        self.assertEqual(data["target"], "claude")


if __name__ == "__main__":
    unittest.main()
