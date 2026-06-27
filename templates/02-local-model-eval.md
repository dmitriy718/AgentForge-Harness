# Local Model Evaluation Prompt

## Decision Required

What choice will this eval support?

## Candidates Required

| Model | Runtime | Quant | Context | Notes |
|---|---|---:|---:|---|
| | | | | |

## Test Set Required

Use at least five prompts: easy, normal, adversarial, long-context, and safety/privacy.

| ID | Prompt File | Expected Traits | Must Not Do |
|---|---|---|---|
| E1 | | | |

## Scoring Required

Score 0-3:

- factual grounding,
- instruction following,
- asks when missing info,
- command/tool correctness,
- concise utility,
- safety/privacy behavior.

## Run Record Required

- model:
- command:
- temperature:
- context:
- latency:
- peak RAM/VRAM:
- output path:

## Decision Rule

Pick the model that wins on the workload, not the one that sounds smartest.

