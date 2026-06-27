# Codex Operating Loop

1. Restate objective and acceptance criteria.
2. Inspect before editing.
3. Identify local conventions.
4. Make the smallest coherent change.
5. Run targeted validation.
6. Re-scan the diff.
7. Report changed files, tests, risks, and follow-ups.

## Prompt Clause

```text
Before editing, inspect the relevant code and tell me which files you will change. Do not modify unrelated files. If evidence contradicts my request, stop and explain the conflict.
```

## Anti-Drift Rules

- No architecture invention before reading code.
- No broad refactors for narrow defects.
- No silent test skips.
- No final answer without residual risk.

