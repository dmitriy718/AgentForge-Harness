# Dmitriy AI Harness

This is an action wrapper for Codex, Claude, local models, or any other LLM. Give it what you want in plain language; it auto-routes the task, adds evidence discipline, adds validation requirements, and executes through Codex when the task needs local code or terminal work.

## Use It

```bash
aih fix the login bug in this repo
aih prompt "review this PR for security and correctness" --target claude
aih run "design a safer migration plan for the billing database"
```

That is the normal workflow. You should not need to pick a template, fill a form, or manually paste a prompt for Codex work.

## What It Adds

- Automatic task mode: implementation, debugging, review, research, architecture, security, extraction, or eval.
- Automatic target: Codex, Claude, or generic LLM.
- Automatic Codex execution for implementation and debugging requests.
- End-of-run summary with status, run record, final response path, and high-level final message.
- Stronger operating contract: facts, assumptions, unknowns, risks, validation, and handoff.
- Safety gates for high-risk work: production, secrets, auth, databases, deletion, and irreversible changes.
- Collision-safe run records under `runs/` when you want an audit trail.
- Machine-readable `doctor --json` and `manifest --json` output for automation.
- Production release packets with doctor output, manifest, self-test logs, validation notes, limitations, support notes, and an example prompt.

## Contents

- `HOW_TO_USE.md`: short operating manual.
- `templates/`: prompts for implementation, debugging, review, research, architecture, security, extraction, evals, and handoffs.
- `playbooks/`: repeatable work loops for Codex, local model testing, and upgrade time.
- `protocols/`: production readiness, evidence discipline, and model routing rules.
- `rubrics/`: scoring systems for outputs and model evals.
- `packs/`: reusable prompt/product packs.
- `swarm/`: agent roles and routing rules.
- `checklists/`: validation and hallucination controls.
- `scripts/aih`: command helper, symlinked as `aih`.
- `runs/`: work records and task outputs.

## Non-Negotiable Rule

For serious work, do not ask a raw model a raw question. Run the request through `aih` first.

## CLI

```bash
aih your request here
aih do "your request here"
aih prompt "your request here"
aih ask "your request here"
aih run "your request here"
aih list
aih show implementation
aih new-run task-name
aih compile implementation /path/to/task-brief.md --out /path/to/prompt.md
aih doctor
aih doctor --json
aih doctor --strict
aih manifest --json
aih release "candidate name"
aih health
```
