Implemented a real production-readiness pass on the harness CLI.

Changed files:
- [scripts/aih](/home/dima/AI-Harness/scripts/aih:18): portable root detection, collision-safe run directories, secret-like request redaction in saved `request.txt`, clean version parsing, expanded `doctor`, `doctor --json`, `doctor --strict`, and new `manifest --json`.
- [tests/test_aih.py](/home/dima/AI-Harness/tests/test_aih.py:60): added regression coverage for run record uniqueness, redaction, classic `new-run` uniqueness, and manifest output.
- [HOW_TO_USE.md](/home/dima/AI-Harness/HOW_TO_USE.md:33) and [INDEX.md](/home/dima/AI-Harness/INDEX.md:22): documented the new production surfaces.
- [VERSION.md](/home/dima/AI-Harness/VERSION.md:3): bumped to `1.2.0-production-cli`.

Validation run:
- `python3 -m unittest discover -s tests -v` → 7 tests passed.
- `scripts/aih doctor --strict` → all checks OK, including Codex CLI and harness skill.
- `scripts/aih manifest --json | python3 -m json.tool` → valid JSON manifest.

Facts: this directory is not a Git repository, so I could not use `git diff` or commit/rollback metadata. Assumption: keeping the existing single-file CLI architecture is the safest improvement path for this turn. Residual risk: the tests mock Codex execution with `/bin/true`; I validated Codex is installed, but I did not launch a live Codex task from inside this turn.

Recovery path if needed: revert the four edited product files plus the test file listed above to their prior contents from your backup/snapshot. No destructive operations, secrets changes, production restarts, or data deletion were performed.