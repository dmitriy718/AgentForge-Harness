# Local Model Lab

## Hardware-Aware Defaults

- CPU: Intel Core Ultra 9 185H, 22 logical CPUs.
- RAM: 30 GiB.
- GPU: Intel Arc integrated graphics.
- Target: smaller instruct/coder models and quantized GGUF models. Do not assume large GPU VRAM.

## Eval Dimensions

- Coding repair on a small repo bug.
- Long-context summarization over local docs.
- Shell command planning with safety boundaries.
- Structured JSON extraction.
- Refusal and privacy behavior.

## Discipline

- Fixed temperature across candidates.
- Identical prompts.
- Save raw outputs.
- Score with `templates/02-local-model-eval.md`.
- Prefer consistent useful performance over one impressive sample.

