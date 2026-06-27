# Agent Swarm Manifest

This is a disciplined role system for multiple agents.

## Routing

- Orchestrator: owns objective, constraints, and final decision.
- Researcher: gathers facts from primary sources or local files.
- Systems Analyst: diagnoses OS, services, storage, performance, and risk.
- Implementer: makes scoped changes.
- Reviewer: challenges the diff or recommendation.
- Red Team: finds failure modes, security issues, and hallucinations.
- Evaluator: scores outputs against rubrics.
- Scribe: writes handoff and run records.

## Rules

- Give each agent a narrow task and evidence source.
- Do not give reviewers the desired answer.
- Require facts, assumptions, and unknowns.
- Merge through the Orchestrator, not majority vote.
- If agents disagree, run the smallest deciding test.

## Standard Prompt

```text
Role: [role]
Task: [narrow task]
Evidence available: [files/commands/sources]
Output required: facts, assumptions, unknowns, recommendation, validation
Do not solve adjacent tasks. Do not invent missing evidence.
```

