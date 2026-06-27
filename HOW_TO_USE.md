# How To Use The Dmitriy AI Harness

The harness is now an action wrapper, not a paperwork system. You give it a plain request. If the request routes to Codex, it runs Codex with a stronger operating prompt. If you only want the prompt, use `aih prompt` or `aih ask`.

## The Normal Workflow

```bash
aih fix the checkout test failure in this repo
```

For implementation and debugging work, this executes through `codex exec` in the current directory and saves a run record.

When Codex finishes, `aih` prints an end-of-run summary with status, request, mode/target/risk, run directory, final response path, and a short high-level summary from Codex's saved final message.

Use `prompt` or `ask` when you want to print the strengthened prompt without executing it:

```bash
aih prompt "review this diff for correctness and security" --target claude
aih ask "debug why docker compose is failing" --target codex
aih prompt "research the current OpenAI Responses API docs" --mode research
```

Use `run` when the work matters enough to keep a record:

```bash
aih run "design a rollback-safe migration for the billing database"
```

This creates:

- `runs/YYYY-MM-DD-task/prompt.md`
- `runs/YYYY-MM-DD-task/request.txt`
- `runs/YYYY-MM-DD-task/metadata.txt`
- `runs/YYYY-MM-DD-task/codex-final.md` for executed Codex runs

Repeated runs with the same request get a numbered suffix instead of overwriting earlier evidence. Secret-like values in `request.txt` are redacted; the generated prompt still contains the original request so execution behavior is unchanged.

## What The Overlay Does

It automatically decides:

- task mode: implementation, debugging, review, research, architecture, security, extraction, or model eval;
- target: Codex, Claude, or generic LLM. Implementation and debugging default to Codex because they usually need files, commands, and tests;
- risk level: normal, medium, or high;
- operating rules: inspect first, separate facts from assumptions, validate, report risk, and stop before irreversible actions.

## The Three Commands That Matter

```bash
aih <plain request>
aih do <plain request>
aih prompt <plain request>
aih ask <plain request> --target codex|claude|generic --mode auto
aih run <plain request>
```

Everything else is advanced.

## Advanced Commands

```bash
aih list
aih show implementation
aih show validation
aih new-run task-name
aih compile implementation runs/YYYY-MM-DD-task/task-brief.md --out runs/YYYY-MM-DD-task/prompt.md
aih doctor
aih doctor --json
aih doctor --strict
aih manifest --json
aih release "candidate name"
aih health
```

The old template workflow still exists for cases where you want maximum control, but it is no longer the default path.

Use `doctor --json` and `manifest --json` when another script or agent needs to verify the harness before relying on it.
Use `release` before treating the harness as a shipped product; it writes a production readiness packet under `runs/releases/` and fails if required diagnostics or self-tests fail.

## Examples

Code work:

```bash
aih fix the failing user import tests and keep changes minimal
```

Debugging:

```bash
aih why is the local API returning 502 after login
```

Review:

```bash
aih ask "review the auth changes for bugs, security issues, and missing tests" --mode review
```

Research:

```bash
aih ask "find the current best way to stream responses with the OpenAI API" --mode research
```

Architecture:

```bash
aih ask "choose between Postgres queues and Redis queues for background jobs" --mode architecture
```

Security:

```bash
aih ask "threat model this webhook ingestion flow" --mode security
```

## Rule Of Thumb

If the model will touch code, data, money, auth, production, or a customer-facing decision, run the request through `aih` first.
