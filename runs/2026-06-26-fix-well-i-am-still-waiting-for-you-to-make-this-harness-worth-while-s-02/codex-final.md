**Summary**

Status: done. I upgraded the harness from “prompt wrapper with docs” to a more productized CLI with release evidence generation, self-test validation, and documented production-readiness workflow.

**What Changed**

- Added `aih release "candidate name"` in [scripts/aih](/home/dima/AI-Harness/scripts/aih:752).
- Release packets now include:
  `doctor.json`, `manifest.json`, `self-test.log`, `validation.md`, `known-limitations.md`, `support-note.md`, `example-prompt.md`.
- Added reusable doctor/manifest payload builders and release gates.
- Added `tests/__init__.py` so `python3 -m unittest` now discovers tests from repo root.
- Added regression coverage for release packet creation in [tests/test_aih.py](/home/dima/AI-Harness/tests/test_aih.py:145).
- Updated docs/version:
  - [INDEX.md](/home/dima/AI-Harness/INDEX.md:25)
  - [HOW_TO_USE.md](/home/dima/AI-Harness/HOW_TO_USE.md:77)
  - [RELEASE_CHECKLIST.md](/home/dima/AI-Harness/RELEASE_CHECKLIST.md:1)
  - [protocols/production-readiness.md](/home/dima/AI-Harness/protocols/production-readiness.md:1)
  - [VERSION.md](/home/dima/AI-Harness/VERSION.md:1)

**Release Evidence**

Created a real release packet at:

`/home/dima/AI-Harness/runs/releases/2026-06-26-1-3-0-release-packets`

The directory date is local New York date; the validation file records UTC creation time.

**Validation**

Passed:

- `python3 -m unittest -v`  
  9 tests passed.
- `python3 -m unittest discover -s tests -v`  
  9 tests passed.
- `scripts/aih doctor --strict`  
  all checks OK, including Codex CLI and release records directory.
- `scripts/aih manifest --json`  
  reports version `1.3.0-release-packets` and includes `release`.
- `scripts/aih release "1.3.0 release packets"`  
  created the production readiness packet successfully.
- Smoke-checked high-risk prompt routing with `scripts/aih prompt "fix production auth bug"`.

**Facts / Assumptions / Unknowns**

Facts: this workspace is not a Git repository, so I could not use `git diff` or provide a commit-style status. The harness CLI and tests validate locally.

Assumption: production-readiness for this file-based harness is best improved by making releases verifiable and repeatable, not by adding unrelated infrastructure.

Unknown: there is still no CI or install/package workflow here; validation is local CLI-based.

**Rollback**

Because this is not a Git repo, rollback is manual: remove `/home/dima/AI-Harness/runs/releases/2026-06-26-1-3-0-release-packets` and restore the edited files listed above from your previous copy/snapshot. Then run `scripts/aih doctor --strict` and `python3 -m unittest -v` to verify recovery.