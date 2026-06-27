## Deep Execution Plan
This request is broad enough to require visible orchestration instead of a single opaque pass.

1. Pass 0 - scope and evidence: inspect the codebase, identify runnable validation, and write concrete acceptance criteria.
2. Pass 1 - comprehensive code review: find correctness, reliability, security, UX, and maintainability issues with file/line evidence where possible.
3. Pass 2 - amateur perspective: look for confusing behavior, unclear commands, surprising output, and missing guardrails.
4. Pass 3 - senior developer perspective: look for bugs, brittle abstractions, missing tests, error handling gaps, and maintainability issues.
5. Pass 4 - systems architect perspective: look for workflow boundaries, state management, integration surfaces, observability, and failure recovery.
6. Pass 5 - CEO/product perspective: look for marketability, time-to-value, user trust, clarity, and support burden.
7. Improvement 1 - implement one high-impact function or capability, then validate it before continuing.
8. Improvement 2 - implement one separate high-impact function or capability, then validate it before continuing.
9. Improvement 3 - implement one separate high-impact function or capability, then validate it before continuing.
10. Final verification - rerun all available validation, review changed code, summarize remaining risks, and stop after one clean final pass or a concrete blocker.

## Deep Execution Rules
- Print progress at the start and end of each pass.
- Keep the loop bounded: do not recurse forever on phrases like 'until zero mistakes'. Stop after the final verification pass if no actionable findings remain.
- If new findings appear, fix only actionable, verified issues. Do not invent work to satisfy the loop.
- Add exactly three new functions or capabilities unless fewer are justified by evidence; validate after each one.
- Preserve the user's prompt content. Do not censor intent; only add safety against execution errors, lost work, unclear state, and unverifiable claims.
