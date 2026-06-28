# AI-Harness User Guide

## What is AI-Harness?

AI-Harness (`aih`) is a command-line tool that wraps your requests to AI coding assistants with **evidence discipline**, **safety gates**, and **audit trails**. It takes a plain English request, intelligently routes it, generates a structured overlay prompt, and (optionally) executes it through Codex or another AI agent.

---

## Installation

### From Source (Editable)

```bash
cd AI-Harness
pip install -e .
```

### Verify Installation

```bash
aih doctor
```

This runs a health check confirming all required files, directories, and dependencies are in place.

### Autocomplete

For Bash or Zsh, source the autocomplete script in your `~/.bashrc` or `~/.zshrc`:

```bash
source /path/to/AI-Harness/scripts/aih-completion.sh
```

---

## Quick Start

### 1. Generate a Prompt

```bash
aih prompt fix the login bug
```

This prints a fully-structured overlay prompt to stdout — ready to paste into any LLM.

### 2. Execute via Codex

```bash
aih do fix the login bug
```

This generates the overlay prompt, saves a run record, and executes through the Codex CLI.

### 3. Preview Routing (Dry Run)

```bash
aih route fix the harness --json
```

Output:
```json
{
  "mode": "implementation",
  "target": "codex",
  "risk": "normal",
  "deep_execution": false
}
```

---

## Commands

| Command | Description |
|---------|-------------|
| `aih do <request>` | Generate prompt + execute via Codex |
| `aih ask <request>` | Generate prompt + print (no execution) |
| `aih prompt <request>` | Alias for `ask` — print the overlay prompt |
| `aih route <request>` | Preview routing decision (mode/target/risk) |
| `aih run <request>` | Save a run record without executing |
| `aih new-run <request>` | Create a new run directory with templates |
| `aih latest-run` | Show the most recent run record |
| `aih doctor` | Run health checks on the harness |
| `aih manifest` | Show the public command surface |
| `aih validate` | Full validation: doctor + self-tests + manifest |
| `aih release <name>` | Generate a release validation packet |
| `aih health` | Write a system health snapshot |
| `aih install-shell` | Install zsh punctuation-safe options |
| `aih list` | List all indexed harness files |
| `aih show <query>` | Display a specific harness file |
| `aih compile <request>` | Compile a full brief from templates |

### Common Flags

- `--json` — Machine-readable JSON output (available on `route`, `doctor`, `manifest`, `validate`, `latest-run`)
- `--mode <mode>` — Override auto-detected mode (`implementation`, `debug`, `review`, `research`, `architecture`, `security`, `extraction`, `eval`)
- `--target <target>` — Override auto-detected target (`codex`, `claude`, `generic`)
- `--dry-run` — Preview what would happen without executing
- `--strict` — Enable strict validation (for `doctor` and `validate`)
- `--file <path>` — Read the request from a file instead of CLI arguments
- `-v`, `--version` — Show the program's version number and exit

---

## Modes

AI-Harness auto-detects the best mode based on keywords in your request:

| Mode | Use Case | Route |
|------|----------|-------|
| **Implementation** | Building, fixing, refactoring code | Codex |
| **Debug** | Diagnosing crashes, errors, failures | Codex |
| **Review** | Code review, PR review, audits | Reasoning model or Codex |
| **Research** | Looking up docs, comparing options | Web-capable model |
| **Architecture** | Design decisions, migration plans | Reasoning model |
| **Security** | Threat modeling, auth review | Reasoning model + red-team |
| **Extraction** | Parsing data, CSV/JSON extraction | Structured-output model |
| **Eval** | Model benchmarks, prompt testing | Repeatable local runs |

---

## Risk Assessment

Requests are automatically classified by risk level:

| Level | Trigger Keywords | Behavior |
|-------|-----------------|----------|
| **High** | `production`, `payment`, `delete`, `database`, `secret`, `credential`, `security`, `auth`, `customer`, `medical`, `legal`, `financial` | Adds safety clauses — stops before destructive operations, requires rollback steps |
| **Medium** | `deploy`, `migration`, `refactor`, `install`, `upgrade`, `permission`, `api` | Calls out migration/compatibility risks |
| **Normal** | Everything else | Standard operating contract |

---

## Deep Execution

When your request is broad or complex (e.g., "comprehensive codebase review from multiple perspectives"), AIH automatically activates **Deep Execution Mode**, which:

1. Generates a multi-pass execution plan (10 passes covering different perspectives)
2. Adds bounded loop rules to prevent infinite recursion
3. Includes three improvement steps with validation after each

Deep execution triggers when:
- The request exceeds 500 characters (configurable via `deep_threshold`), OR
- The request contains ≥ 2 deep-request terms (e.g., "comprehensive", "senior developer", "all findings", "zero mistakes") or terms defined in `custom_deep_terms` in your config file.

---

## Configuration

### Config File Locations

1. `~/.config/ai-harness/config.toml` (user-level)
2. `.aih.toml` (project-level, higher priority)

### Available Settings

```toml
# Default routing target
target = "auto"  # "codex", "claude", "generic", or "auto"

# Default mode
mode = "auto"  # or any specific mode name

# Path to Codex CLI binary
codex_bin = ""

# Terminal color mode
color = "auto"  # "always", "never", or "auto"

# Deep execution threshold (characters)
deep_threshold = 500

# Minimum deep-request terms to trigger deep execution
deep_min_terms = 2

# Custom keywords to trigger deep execution
custom_deep_terms = ["corporate standard", "zero defects"]

# Router model (stub = keyword classifier, future: LLM model name)
router_model = "stub"

# Override harness root directory
harness_home = ""
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `AI_HARNESS_HOME` | Override the harness root directory |
| `AIH_CODEX_BIN` | Path to the Codex CLI binary |
| `AIH_COLOR` | Color mode (`always`, `never`, `auto`) |
| `NO_COLOR` | Disable colors (standard convention) |
| `AIH_AGENT_API_KEY` | API key for intelligent routing / agent operations |
| `AIH_OPENAI_BASE_URL` | Base URL for the OpenAI-compatible REST API (defaults to `https://api.openai.com/v1`) |

---

## Run Records

Every execution creates a timestamped run record under `runs/`:

```
runs/2026-06-28-fix-the-login-bug/
├── prompt.md          # The generated overlay prompt
├── request.txt        # Redacted version of the original request
├── metadata.txt       # Mode, target, risk, version, timestamp
├── execution-plan.md  # (Only for deep execution requests)
└── codex-final.md     # (Only after Codex execution completes)
```

Secret-like values (API keys, passwords, tokens) are automatically **redacted** from `request.txt`.

---

## Troubleshooting

### `aih doctor` shows failures

Run `aih doctor --strict --json` for detailed diagnostics. Common fixes:

- **root exists**: Set `AI_HARNESS_HOME` to the correct path
- **aih executable**: Ensure `scripts/aih` exists and is executable
- **harness files indexed**: Check that template/playbook directories contain `.md` files

### Codex execution fails

1. Check that `codex` CLI is installed: `which codex`
2. Set `AIH_CODEX_BIN` if codex is in a non-standard location
3. Inspect the run record (especially `prompt.md` and `metadata.txt`)

### Import errors

Run `pip install -e .` to ensure all dependencies (including `pydantic>=2.0`) are installed.

---

## Security

AI-Harness includes built-in security features:

- **Request sanitization**: Shell injection patterns (backticks, `$()`, pipe-to-destructive commands) are blocked
- **Secret redaction**: API keys, passwords, and tokens are automatically redacted from run records
- **Audit logging**: All security events are logged to `~/.config/ai-harness/logs/audit.jsonl`
- **Input validation**: Request length limits (50,000 chars max) prevent abuse

---

## FAQ

**Q: Can I use AIH without Codex?**
A: Yes. `aih prompt`, `aih ask`, and `aih route` work without Codex. Only `aih do` requires the Codex CLI.

**Q: How do I add a new mode?**
A: Add an entry to `MODES` in `aih/constants.py` with `title`, `route`, and `keywords`.

**Q: Where are logs stored?**
A: Audit logs go to `~/.config/ai-harness/logs/audit.jsonl`. Run records go to `<harness_root>/runs/`.
