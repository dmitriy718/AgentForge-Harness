# Known Limitations

- `aih` depends on the Codex CLI for automatic execution; without it, prompt generation still works.
- `aih health` records local system diagnostics and may include machine-specific package, disk, or service names.
- Secret-like values are redacted from `request.txt`, but generated prompts retain the original request so execution context is preserved.
