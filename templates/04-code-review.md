# Code Review Prompt

Review as a senior engineer. Prioritize correctness, security, data loss, performance, and missing tests.

## Scope Required

- Diff source:
- In scope:
- Out of scope:

## Product Intent Required

What should the change accomplish?

## Rules

- Findings first, ordered by severity.
- Every finding needs file/line evidence.
- No style nits unless they hide real risk.
- If there are no findings, say so and identify residual test gaps.

## Output Required

```text
Findings
- Severity:
  File:
  Issue:
  Evidence:
  Fix:

Open Questions

Test Gaps

Summary
```

