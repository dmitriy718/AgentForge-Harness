"""Unit tests for aih.routing — direct imports, no subprocess."""

from __future__ import annotations

import unittest
from pathlib import Path

from aih.routing import Overlay, classify_mode, choose_target, infer_risk, is_deep_request


class ClassifyModeTests(unittest.TestCase):
    def test_fix_routes_to_implementation(self) -> None:
        self.assertEqual(classify_mode("fix the harness script"), "implementation")

    def test_debug_routes_to_debug(self) -> None:
        self.assertEqual(classify_mode("debug docker compose login failure"), "debug")

    def test_review_routes_to_review(self) -> None:
        self.assertEqual(classify_mode("review this PR for security issues"), "review")

    def test_research_routes_to_research(self) -> None:
        self.assertEqual(classify_mode("research the latest OpenAI API docs"), "research")

    def test_architecture_routes_to_architecture(self) -> None:
        self.assertEqual(classify_mode("choose between postgres and redis for queues"), "architecture")

    def test_security_routes_to_security(self) -> None:
        self.assertEqual(classify_mode("threat model this auth flow"), "security")

    def test_extraction_routes_to_extraction(self) -> None:
        self.assertEqual(classify_mode("extract data into csv"), "extraction")

    def test_eval_routes_to_eval(self) -> None:
        self.assertEqual(classify_mode("benchmark this ollama model"), "eval")

    def test_explicit_mode_overrides_classification(self) -> None:
        self.assertEqual(classify_mode("fix the bug", "review"), "review")

    def test_unknown_mode_raises(self) -> None:
        with self.assertRaises(SystemExit):
            classify_mode("hello", "nonexistent")

    def test_empty_request_defaults_to_implementation(self) -> None:
        self.assertEqual(classify_mode("hello world"), "implementation")


class InferRiskTests(unittest.TestCase):
    def test_production_is_high_risk(self) -> None:
        self.assertEqual(infer_risk("deploy to production"), "high")

    def test_database_is_high_risk(self) -> None:
        self.assertEqual(infer_risk("migrate the database"), "high")

    def test_deploy_is_medium_risk(self) -> None:
        self.assertEqual(infer_risk("deploy to staging"), "medium")

    def test_refactor_is_medium_risk(self) -> None:
        self.assertEqual(infer_risk("refactor the login module"), "medium")

    def test_fix_test_is_normal_risk(self) -> None:
        self.assertEqual(infer_risk("fix the unit test"), "normal")


class ChooseTargetTests(unittest.TestCase):
    def test_implementation_mode_routes_to_codex(self) -> None:
        self.assertEqual(choose_target("anything", "auto", "implementation"), "codex")

    def test_debug_mode_routes_to_codex(self) -> None:
        self.assertEqual(choose_target("anything", "auto", "debug"), "codex")

    def test_explicit_target_overrides(self) -> None:
        self.assertEqual(choose_target("anything", "claude", "implementation"), "claude")

    def test_claude_keywords_route_to_claude(self) -> None:
        self.assertEqual(choose_target("brainstorm ideas", "auto", "research"), "claude")

    def test_codex_keywords_route_to_codex(self) -> None:
        self.assertEqual(choose_target("fix this repo", "auto", "review"), "codex")

    def test_generic_fallback(self) -> None:
        self.assertEqual(choose_target("what is the meaning of life", "auto", "research"), "generic")


class IsDeepRequestTests(unittest.TestCase):
    def test_short_simple_request_is_not_deep(self) -> None:
        self.assertFalse(is_deep_request("fix the bug"))

    def test_long_request_is_deep(self) -> None:
        self.assertTrue(is_deep_request("x" * 500))

    def test_two_deep_terms_is_deep(self) -> None:
        self.assertTrue(is_deep_request("comprehensive review from senior developer perspective"))

    def test_one_deep_term_is_not_deep(self) -> None:
        self.assertFalse(is_deep_request("comprehensive review"))

    def test_custom_threshold(self) -> None:
        self.assertTrue(is_deep_request("x" * 100, threshold=100))
        self.assertFalse(is_deep_request("x" * 99, threshold=100))


class OverlayTests(unittest.TestCase):
    def test_overlay_is_frozen(self) -> None:
        o = Overlay(request="test", mode="implementation", target="codex", cwd=Path("."), risk="normal")
        with self.assertRaises(AttributeError):
            o.mode = "review"  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
