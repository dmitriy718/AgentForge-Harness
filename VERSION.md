# Version

Current version: `1.3.0-release-packets`

## 1.3.0-release-packets

- Added `aih release "candidate name"` to create production readiness evidence under `runs/releases/`.
- Release packets now include doctor output, manifest, self-test logs, validation notes, known limitations, support notes, and an example prompt.
- Made `python3 -m unittest` discover the test suite from the repository root.
- Added regression coverage for release packet generation and updated the manifest command surface.

## 1.2.1-completion-summary

- Added a completion footer after Codex execution so `aih` ends with status, run record, final response path, and a high-level summary.
- Captured completion timestamp and exit code in run metadata.
- Added regression coverage for the completion summary and captured final response.

## 1.2.0-production-cli

- Made harness root detection portable when `AI_HARNESS_HOME` is not set.
- Made saved run records collision-safe so repeated requests do not overwrite audit evidence.
- Redacted secret-like values from saved `request.txt` files while preserving the full prompt for execution context.
- Added `aih manifest` with JSON output for automation and integration checks.
- Expanded `aih doctor` with core file checks, duplicate detection, optional strict mode, and JSON output.
- Added regression coverage for audit record uniqueness, redaction, and the manifest command.

## 1.1.0-action-wrapper

- Made plain `aih <request>` execute through `codex exec` when the request routes to Codex.
- Added `aih do` for explicit execution and `aih prompt` for prompt-only output.
- Saved execution run records with the generated prompt and Codex final response path.
- Added regression coverage for the execution wrapper without launching a real Codex session.

## 1.0.1-overlay-routing

- Fixed implementation and debugging requests so they auto-route to Codex by default.
- Added stronger action bias so agents do the work instead of stopping at a plan when tools are available.
- Added explicit working notes for facts, assumptions, unknowns, and validation.
- Added regression tests for routing and prompt quality.

## 1.0.0-overlay

- Made the primary interface `aih <plain request>`.
- Added automatic mode routing for implementation, debugging, review, research, architecture, security, extraction, and eval work.
- Added automatic target routing for Codex, Claude, and generic LLMs.
- Added risk detection and high-risk safety gates.
- Added `aih run` for one-command prompt generation with an audit trail.
- Kept the old template workflow as advanced mode instead of the default path.

## 0.2.0-local-production

- Added Python `aih` CLI.
- Added detailed usage guide.
- Added production readiness, evidence, and model routing protocols.
- Added quality and model evaluation rubrics.
- Added local model benchmark pack.
- Added Codex power pack.
- Added market-ready prompt product pack.
