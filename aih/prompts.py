"""Overlay prompt generation."""

from __future__ import annotations

from aih.constants import MODES
from aih.routing import Overlay, is_deep_request


def overlay_clauses(mode: str, target: str, risk: str) -> list[str]:
    clauses = [
        "Restate the objective in one sentence before acting.",
        "Treat the request as an outcome to deliver, not a topic to discuss.",
        "Do not stop at a plan when the user asked you to fix, build, change, debug, or review something and you have the tools to act.",
        "Separate facts, assumptions, unknowns, and inferences.",
        "Use available evidence first. Do not invent missing context.",
        "When context is missing, make the smallest safe assumption and say how to verify it.",
        "Prefer direct inspection, tests, primary sources, and reproducible commands over plausible explanations.",
        "Before finalizing, run or specify validation that could falsify the answer.",
        "If blocked, state the blocker, the exact missing input, and the smallest useful next step.",
    ]

    if target == "codex":
        clauses.extend(
            [
                "Inspect the local workspace before editing.",
                "Preserve unrelated user changes.",
                "Keep edits scoped to the requested behavior.",
                "Report changed files, commands run, and residual risk.",
            ]
        )
    elif target == "claude":
        clauses.extend(
            [
                "Think through edge cases explicitly.",
                "Use concise reasoning summaries instead of hidden leaps.",
                "Return an answer that can be handed to an implementation agent if code changes are needed.",
            ]
        )
    else:
        clauses.extend(
            [
                "Use the strongest available tools for the job.",
                "Return a self-contained result that another model or human can verify.",
            ]
        )

    if mode == "debug":
        clauses.extend(
            [
                "Rank likely causes by evidence.",
                "Run the smallest discriminating check before proposing broad fixes.",
            ]
        )
    elif mode == "review":
        clauses.extend(
            [
                "Lead with findings ordered by severity.",
                "Every finding needs evidence, impact, and a concrete fix.",
            ]
        )
    elif mode == "research":
        clauses.extend(
            [
                "Browse or cite primary/current sources when facts may have changed.",
                "Distinguish quoted source facts from your synthesis.",
            ]
        )
    elif mode == "architecture":
        clauses.extend(
            [
                "Compare at least two viable options.",
                "State the decision, why it wins, and what would change the decision.",
            ]
        )
    elif mode == "security":
        clauses.extend(
            [
                "Map assets, trust boundaries, attack paths, and mitigations.",
                "Include a red-team pass against your own recommendation.",
            ]
        )
    elif mode == "extraction":
        clauses.extend(
            [
                "Define the output schema before extracting.",
                "Validate malformed, missing, and ambiguous fields.",
            ]
        )
    elif mode == "eval":
        clauses.extend(
            [
                "Keep prompts, temperature, inputs, and scoring consistent.",
                "Record raw outputs before judging them.",
            ]
        )
    else:
        clauses.extend(
            [
                "Identify the local pattern before changing implementation.",
                "Finish with targeted validation and a concise handoff.",
            ]
        )

    if risk == "high":
        clauses.extend(
            [
                "Stop before destructive operations, secrets changes, production restarts, data deletion, or irreversible actions.",
                "Provide rollback or recovery steps for every risky change.",
            ]
        )
    elif risk == "medium":
        clauses.append("Call out migration, deployment, permission, and compatibility risks before acting.")

    return clauses


def deep_pass_plan(request: str) -> list[str]:
    return [
        "Pass 0 - scope and evidence: inspect the codebase, identify runnable validation, and write concrete acceptance criteria.",
        "Pass 1 - comprehensive code review: find correctness, reliability, security, UX, and maintainability issues with file/line evidence where possible.",
        "Pass 2 - amateur perspective: look for confusing behavior, unclear commands, surprising output, and missing guardrails.",
        "Pass 3 - senior developer perspective: look for bugs, brittle abstractions, missing tests, error handling gaps, and maintainability issues.",
        "Pass 4 - systems architect perspective: look for workflow boundaries, state management, integration surfaces, observability, and failure recovery.",
        "Pass 5 - CEO/product perspective: look for marketability, time-to-value, user trust, clarity, and support burden.",
        "Improvement 1 - implement one high-impact function or capability, then validate it before continuing.",
        "Improvement 2 - implement one separate high-impact function or capability, then validate it before continuing.",
        "Improvement 3 - implement one separate high-impact function or capability, then validate it before continuing.",
        "Final verification - rerun all available validation, review changed code, summarize remaining risks, and stop after one clean final pass or a concrete blocker.",
    ]


def deep_execution_block(request: str) -> str:
    if not is_deep_request(request):
        return ""

    plan = "\n".join(f"{index + 1}. {step}" for index, step in enumerate(deep_pass_plan(request)))
    return "\n".join(
        [
            "## Deep Execution Plan",
            "This request is broad enough to require visible orchestration instead of a single opaque pass.",
            "",
            plan,
            "",
            "## Deep Execution Rules",
            "- Print progress at the start and end of each pass.",
            "- Keep the loop bounded: do not recurse forever on phrases like 'until zero mistakes'. Stop after the final verification pass if no actionable findings remain.",
            "- If new findings appear, fix only actionable, verified issues. Do not invent work to satisfy the loop.",
            "- Add exactly three new functions or capabilities unless fewer are justified by evidence; validate after each one.",
            "- Preserve the user's prompt content. Do not censor intent; only add safety against execution errors, lost work, unclear state, and unverifiable claims.",
        ]
    )


def build_prompt(overlay: Overlay) -> str:
    mode_spec = MODES[overlay.mode]
    clauses = "\n".join(f"- {clause}" for clause in overlay_clauses(overlay.mode, overlay.target, overlay.risk))
    cwd_text = str(overlay.cwd)
    deep_block = deep_execution_block(overlay.request)

    parts = [
        "# AI Harness Overlay Prompt",
        "",
        "## User Request",
        overlay.request,
        "",
        "## Auto-Routing",
        f"- Mode: {mode_spec['title']}",
        f"- Target: {overlay.target}",
        f"- Recommended route: {mode_spec['route']}",
        f"- Risk: {overlay.risk}",
        f"- Workspace: {cwd_text}",
        "",
        "## Operating Contract",
        clauses,
        "",
    ]
    if deep_block:
        parts.extend([deep_block, ""])

    parts.extend(
        [
            "## Execution Loop",
            "1. Convert the user request into concrete acceptance criteria.",
            "2. Gather only the context needed to act correctly.",
            "3. State facts, assumptions, unknowns, and risks before committing to a direction.",
            "4. Do the work or produce the requested artifact.",
            "5. Run the most relevant validation available; if validation cannot run, explain why and provide a substitute check.",
            "6. Self-review the result for missed requirements, weak assumptions, and avoidable complexity.",
            "7. Final answer: outcome, evidence, validation, risks, and next action if any.",
            "",
            "## Required Working Notes",
            "- Facts: observed evidence only.",
            "- Assumptions: what you are taking as true, with confidence.",
            "- Unknowns: what remains unverified and whether it matters.",
            "- Validation: commands, checks, sources, or examples used to falsify the result.",
            "",
            "## Output Shape",
            "Start with a high-level summary and current status. Then use the shortest format that fully handles the task. For code work, include changed files and tests. For review, include findings first. For research, include source links. For plans, include ordered steps and decision criteria.",
            "",
        ]
    )
    return "\n".join(parts)
