# Hallucination Control Checklist

Before trusting an AI output, verify:

- It separates facts from assumptions.
- It cites local evidence or primary sources for important claims.
- It marks stale-prone claims.
- It does not invent files, APIs, flags, packages, or command output.
- It asks for missing high-risk input instead of guessing.
- It includes verification that can fail.
- It includes rollback for destructive changes.
- It preserves your constraints.
- It gives the smallest useful next action.

Use this clause when accuracy matters:

```text
Do not fill gaps with plausible guesses. Mark unknowns explicitly and tell me the fastest way to verify them.
```

