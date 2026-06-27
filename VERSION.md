# Version

Current version: `2.0.0-modular-foundation`

## 2.0.0-modular-foundation

- Restructured the monolithic `scripts/aih` (1,272 lines) into a modular `aih/` Python package with 11 focused modules: `cli`, `routing`, `prompts`, `audit`, `doctor`, `display`, `config`, `constants`, `release`, `health`, and `shell`.
- Added `pyproject.toml` for pip-installable distribution with `aih` console entry point.
- Added `python3 -m aih` invocation support.
- Added `--dry-run` flag to `aih do` for previewing routing and prompt before execution.
- Added configuration file support via `~/.config/ai-harness/config.toml` and per-project `.aih.toml`.
- Added 74 unit tests across 5 test modules (`test_routing`, `test_prompts`, `test_audit`, `test_display`, `test_config`, `test_doctor`) for direct function-level testing.
- Maintained full backward compatibility: `scripts/aih` wrapper and all 23 original integration tests pass unchanged.
- Fixed timezone-naive `datetime.now()` in `compile` command (now uses UTC).
- Total test suite: 97 tests passing in under 2 seconds.

## 1.5.0-operator-safety-tools

- Added `aih route` to preview mode, target, risk, and deep-execution detection without generating or executing a prompt.
- Added `aih validate` to run doctor checks, self-tests, and manifest generation as one validation gate.
- Added `aih latest-run` to locate the newest saved run record and key evidence paths.
- Added prompt-only warnings for `aih prompt --out`, `aih prompt --save`, and record-only warnings for `aih run`.
- Added color-aware human terminal summaries with `AIH_COLOR` and `NO_COLOR` controls while preserving plain JSON output.
- Optimized route previews, latest-run lookup, duplicate-name checks, and deep-plan persistence to avoid unnecessary prompt builds, full sorts, quadratic scans, and repeated plan generation.
- Added regression coverage for route previews, validation gates, latest-run lookup, and non-executing output modes.

## 1.4.1-prompt-mode-hint

- Added a prompt-only warning when `aih prompt` or `aih ask` generates Codex-routed work.
- Added a deep-execution hint for prompt-only broad review/fix requests.
- Kept generated prompt stdout clean for copying while sending execution hints to stderr.
- Added regression coverage for prompt-only execution hints.

## 1.4.0-deep-execution

- Added deep request detection for broad review/fix prompts.
- Added bounded multi-pass execution plans with review perspectives and three one-at-a-time improvements.
- Saved `execution-plan.md` for deep runs and announced the plan before Codex starts.
- Added regression coverage for deep request planning and execution visibility.

## 1.3.1-shell-punctuation

- Added `aih install-shell` to install zsh options that let unquoted punctuation survive in plain-language prompts.
- Documented the zsh punctuation fix for parentheses, brackets, and question marks.
- Added regression coverage for the shell installer and punctuation handling.

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
