# Production Readiness Protocol

Use this before shipping a prompt, agent workflow, script, document, feature, or recommendation outside personal experimentation.

## Gates

1. Clear target user and use case.
2. Repeatable input format.
3. Explicit output contract.
4. Validation method.
5. Failure handling.
6. Safety/privacy boundary.
7. Versioned release notes.
8. Example run.
9. Handoff or support note.

## Release Record

Save a release record in `runs/releases/YYYY-MM-DD-name/` containing:

- prompt or artifact,
- examples,
- validation notes,
- known limitations,
- next version ideas.

For this harness, use:

```bash
aih release "candidate name"
```

The generated packet includes `doctor.json`, `manifest.json`, `self-test.log`, `validation.md`, `known-limitations.md`, `support-note.md`, and `example-prompt.md`.
