# Evidence-Led Prompting Protocol

Use this protocol when hallucination is expensive.

## Required Sections

- Objective
- Evidence
- Assumptions
- Unknowns
- Constraints
- Proposed action
- Validation
- Rollback

## Required Language

```text
Separate facts from assumptions. Do not infer missing command output, files, APIs, versions, laws, prices, or schedules. If something is unknown, mark it unknown and give the fastest verification path.
```

## Confidence Policy

- High: verified locally or in primary source.
- Medium: inferred from multiple consistent signals.
- Low: plausible but unverified.

Any low-confidence claim that affects action must produce a verification step before action.

