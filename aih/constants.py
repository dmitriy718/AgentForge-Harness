"""Shared constants for the AI Harness."""

from __future__ import annotations

import re
from pathlib import Path

SEARCH_DIRS = ["templates", "playbooks", "checklists", "swarm", "protocols", "rubrics", "packs"]
CORE_FILES = [
    "INDEX.md",
    "HOW_TO_USE.md",
    "VERSION.md",
    "scripts/aih",
    "templates/00-universal-task-brief.md",
    "templates/01-codex-implementation.md",
    "templates/03-debug-diagnostic.md",
    "templates/04-code-review.md",
    "templates/07-agent-handoff.md",
    "protocols/production-readiness.md",
    "checklists/validation-gate.md",
]
CORE_DIRS = ["templates", "playbooks", "checklists", "swarm", "protocols", "rubrics", "packs", "runs"]
SHELL_ENV = Path.home() / ".config" / "ai-harness" / "env.sh"
SHELL_BLOCK_BEGIN = "# >>> AIH punctuation-safe prompt input >>>"
SHELL_BLOCK_END = "# <<< AIH punctuation-safe prompt input <<<"
RELEASE_GATES = [
    "clear target user and use case",
    "repeatable input format",
    "explicit output contract",
    "validation method",
    "failure handling",
    "safety/privacy boundary",
    "versioned release notes",
    "example run",
    "handoff or support note",
]
SENSITIVE_REQUEST_PATTERNS = (
    re.compile(r"(?i)\b(sk-[A-Za-z0-9_-]{12,})"),
    re.compile(r"(?i)\b(api[_-]?key|token|password|secret)\s*[:=]\s*\S+"),
)
DEEP_REQUEST_TERMS = (
    "comprehensive",
    "all bugs",
    "all findings",
    "all code",
    "every line",
    "every other line",
    "multiple passes",
    "additional 4 passes",
    "4 passes",
    "different perspective",
    "senior developer",
    "systems architect",
    "ceo",
    "zero mistakes",
    "zero errors",
    "zero warnings",
    "continue to do",
    "until you have a pass",
)
ANSI = {
    "bold": "1",
    "cyan": "36",
    "green": "32",
    "red": "31",
    "yellow": "33",
}
MODES = {
    "implementation": {
        "title": "Implementation",
        "route": "Codex or another coding agent with filesystem and terminal access.",
        "keywords": (
            "aih",
            "build",
            "change",
            "code",
            "edit",
            "feature",
            "fix",
            "harness",
            "implement",
            "patch",
            "refactor",
            "repo",
            "script",
            "test",
            "tool",
        ),
    },
    "debug": {
        "title": "Debugging",
        "route": "Codex for local inspection, logs, commands, and targeted fixes.",
        "keywords": (
            "broken",
            "bug",
            "crash",
            "debug",
            "diagnose",
            "error",
            "fail",
            "fails",
            "issue",
            "log",
            "trace",
        ),
    },
    "review": {
        "title": "Review",
        "route": "A strong reasoning model or Codex when repository context is needed.",
        "keywords": ("audit", "check", "pr", "review", "risk", "vulnerability"),
    },
    "research": {
        "title": "Research",
        "route": "A web-capable model, with primary sources required for unstable facts.",
        "keywords": (
            "compare",
            "current",
            "docs",
            "find",
            "latest",
            "look up",
            "research",
            "source",
            "verify",
        ),
    },
    "architecture": {
        "title": "Architecture",
        "route": "A strong reasoning model, optionally followed by Codex for implementation.",
        "keywords": ("architecture", "choose", "design", "migrate", "plan", "scale", "tradeoff"),
    },
    "security": {
        "title": "Security",
        "route": "A strong reasoning model plus a red-team review pass.",
        "keywords": ("auth", "credential", "exploit", "permission", "privacy", "secret", "security", "threat"),
    },
    "extraction": {
        "title": "Data Extraction",
        "route": "A structured-output model or local script, with schema validation.",
        "keywords": ("csv", "data", "extract", "json", "parse", "spreadsheet", "table"),
    },
    "eval": {
        "title": "Model Evaluation",
        "route": "Repeatable local or hosted model runs scored with the same rubric.",
        "keywords": ("benchmark", "eval", "evaluate", "model", "ollama", "prompt test", "score"),
    },
}
