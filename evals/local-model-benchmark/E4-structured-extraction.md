# E4 Structured Extraction

Extract JSON from this text. Use `null` for missing values.

```text
Host GT1 runs Linux Mint 22.3 on kernel 6.17.0-35-generic. CPU is Intel Core Ultra 9 185H. RAM is 30 GiB. NVMe health passed. GPU VRAM is not reported.
```

Schema:

```json
{
  "host": "string",
  "os": "string",
  "kernel": "string",
  "cpu": "string",
  "ram_gib": "number",
  "nvme_health": "string",
  "gpu_vram_gib": "number|null"
}
```

Return JSON only.

