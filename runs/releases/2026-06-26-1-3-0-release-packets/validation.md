# Release Validation: 1.3.0 release packets

- Created: 2026-06-27T01:04:18+00:00
- Version: 1.3.0-release-packets
- Strict doctor: False
- Doctor passed: True
- Self-tests passed: True

## Production Gates
- [x] clear target user and use case
- [x] repeatable input format
- [x] explicit output contract
- [x] validation method
- [x] failure handling
- [x] safety/privacy boundary
- [x] versioned release notes
- [x] example run
- [x] handoff or support note

## Commands
- `aih doctor --json`
- `python3 -m unittest discover -s tests -v`
- `aih manifest --json`

## Failure Handling
If any required doctor check or self-test fails, do not ship the release. Fix the failed check, rerun `aih release`, and use the newest release packet as evidence.

## Rollback
Keep the previous release packet under `runs/releases/`. Revert to the previous `scripts/aih` and documentation state, then rerun `aih doctor` and the self-tests before using the harness for production work.
