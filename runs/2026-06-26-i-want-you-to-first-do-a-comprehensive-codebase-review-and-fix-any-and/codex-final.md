High-level status: completed the bounded review/fix cycle, added exactly three new AIH capabilities, and the final verification pass is clean.

Changed files:
- [scripts/aih](/home/dima/AI-Harness/scripts/aih:581)
  - Fixed prompt-only guardrails for `prompt --out`, `prompt --save`, and `run`.
  - Added `aih route`.
  - Added `aih validate`.
  - Added `aih latest-run`.
- [tests/test_aih.py](/home/dima/AI-Harness/tests/test_aih.py:122)
  - Added regression coverage for all new capabilities and guardrail fixes.
- [HOW_TO_USE.md](/home/dima/AI-Harness/HOW_TO_USE.md:34), [INDEX.md](/home/dima/AI-Harness/INDEX.md:22), [VERSION.md](/home/dima/AI-Harness/VERSION.md:3)
  - Documented the new command surface and bumped version to `1.5.0-operator-safety-tools`.

The three new capabilities:
1. `aih route "request" --json` previews mode, target, risk, and deep-execution detection.
2. `aih validate --json` runs doctor checks, self-tests, and manifest verification as one gate.
3. `aih latest-run --json` finds the newest saved run record and key evidence paths.

Validation run:
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest` passed: 22 tests.
- `scripts/aih doctor` passed.
- `scripts/aih validate --json` passed earlier with `ok=True`, `doctor_ok=True`, `self_tests_ok=True`.
- `python3 -m py_compile scripts/aih` passed.
- `bash -n scripts/run-local-model-eval scripts/weekly-maintenance scripts/monthly-health-snapshot` passed.
- Manual checks for `route` and `latest-run` passed.

Facts: final local validation is clean.  
Assumption: the pre-existing uncommitted harness changes were intentional, so I preserved and extended them.  
Residual risk: no external CI was available here; validation is local. The pre-existing untracked run directory remains untouched: `runs/2026-06-26-i-want-you-to-first-do-a-comprehensive-codebase-review-and-fix-any-and/`.