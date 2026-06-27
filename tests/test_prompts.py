"""Unit tests for aih.prompts — direct imports, no subprocess."""

from __future__ import annotations

import unittest
from pathlib import Path

from aih.prompts import build_prompt, deep_execution_block, deep_pass_plan, overlay_clauses
from aih.routing import Overlay


class OverlayClausesTests(unittest.TestCase):
    def test_codex_target_adds_workspace_clauses(self) -> None:
        clauses = overlay_clauses("implementation", "codex", "normal")
        self.assertTrue(any("Inspect the local workspace" in c for c in clauses))

    def test_claude_target_adds_reasoning_clauses(self) -> None:
        clauses = overlay_clauses("review", "claude", "normal")
        self.assertTrue(any("edge cases" in c for c in clauses))

    def test_high_risk_adds_safety_clauses(self) -> None:
        clauses = overlay_clauses("implementation", "codex", "high")
        self.assertTrue(any("destructive operations" in c for c in clauses))

    def test_medium_risk_adds_migration_clause(self) -> None:
        clauses = overlay_clauses("implementation", "codex", "medium")
        self.assertTrue(any("migration" in c for c in clauses))

    def test_debug_mode_adds_evidence_clause(self) -> None:
        clauses = overlay_clauses("debug", "codex", "normal")
        self.assertTrue(any("Rank likely causes" in c for c in clauses))

    def test_review_mode_adds_findings_clause(self) -> None:
        clauses = overlay_clauses("review", "codex", "normal")
        self.assertTrue(any("findings ordered by severity" in c for c in clauses))

    def test_security_mode_adds_red_team_clause(self) -> None:
        clauses = overlay_clauses("security", "codex", "normal")
        self.assertTrue(any("red-team" in c for c in clauses))

    def test_no_duplicates_in_clauses(self) -> None:
        clauses = overlay_clauses("architecture", "codex", "normal")
        self.assertEqual(len(clauses), len(set(clauses)))


class DeepExecutionTests(unittest.TestCase):
    def test_deep_pass_plan_has_10_steps(self) -> None:
        self.assertEqual(len(deep_pass_plan("any request")), 10)

    def test_deep_block_returns_empty_for_simple_request(self) -> None:
        self.assertEqual(deep_execution_block("fix the bug"), "")

    def test_deep_block_returns_plan_for_deep_request(self) -> None:
        block = deep_execution_block("comprehensive review from senior developer perspective")
        self.assertIn("Deep Execution Plan", block)
        self.assertIn("Pass 3 - senior developer", block)

    def test_deep_block_includes_rules(self) -> None:
        block = deep_execution_block("comprehensive review from senior developer perspective")
        self.assertIn("Deep Execution Rules", block)


class BuildPromptTests(unittest.TestCase):
    def test_prompt_contains_user_request(self) -> None:
        overlay = Overlay(request="fix the login bug", mode="implementation", target="codex", cwd=Path("/tmp"), risk="normal")
        prompt = build_prompt(overlay)
        self.assertIn("fix the login bug", prompt)

    def test_prompt_contains_mode(self) -> None:
        overlay = Overlay(request="test", mode="implementation", target="codex", cwd=Path("/tmp"), risk="normal")
        prompt = build_prompt(overlay)
        self.assertIn("Mode: Implementation", prompt)

    def test_prompt_contains_operating_contract(self) -> None:
        overlay = Overlay(request="test", mode="debug", target="codex", cwd=Path("/tmp"), risk="normal")
        prompt = build_prompt(overlay)
        self.assertIn("Operating Contract", prompt)

    def test_prompt_contains_execution_loop(self) -> None:
        overlay = Overlay(request="test", mode="implementation", target="codex", cwd=Path("/tmp"), risk="normal")
        prompt = build_prompt(overlay)
        self.assertIn("Execution Loop", prompt)

    def test_deep_request_prompt_contains_deep_plan(self) -> None:
        overlay = Overlay(
            request="comprehensive review from senior developer all findings",
            mode="review", target="codex", cwd=Path("/tmp"), risk="normal",
        )
        prompt = build_prompt(overlay)
        self.assertIn("Deep Execution Plan", prompt)


if __name__ == "__main__":
    unittest.main()
