# AI-Harness Agent Tools

To provide maximum autonomy, AI-Harness equips its agents (`SwarmAgent`) with a suite of 10 highly-optimized tools. These tools were selected through a rigorous utility evaluation to ensure the agent has all the required primitives for software development, debugging, and research, without bloating the system with unnecessary third-party dependencies.

## 1. File I/O Tools

### `read_file(filepath: str)`
Reads the contents of a local file.
- **Why it’s essential:** Allows the agent to inspect source code, configuration files, and logs.
- **Features:** Truncates outputs larger than 20,000 characters to prevent LLM context-window explosions.

### `write_file(filepath: str, content: str)`
Writes text content to a local file, automatically creating parent directories if needed.
- **Why it’s essential:** This is how the agent writes new features, fixes bugs, and scaffolds out projects.

### `list_directory(path: str = ".")`
Lists the files and folders in a given directory.
- **Why it’s essential:** Enables the agent to explore the workspace, discover file names, and understand project structures without needing to blindly guess paths.

## 2. Execution Tools

### `execute_shell(command: str, timeout: int = 30)`
Executes a terminal shell command and captures `stdout` and `stderr`.
- **Why it’s essential:** Provides unlimited extensibility. Agents use this to run `pytest`, `git commit`, `npm install`, or execute compiler checks.
- **Features:** Hard 30-second timeout to prevent the agent from hanging on interactive prompts (like `vim` or `nano`).

### `execute_python(code: str, timeout: int = 30)`
Executes arbitrary Python code in a standalone subprocess sandbox.
- **Why it’s essential:** Allows the agent to mathematically verify logic, process complex data formats, or script temporary solutions *before* committing them to the main codebase. (A far superior alternative to a simple "Calculator" tool).

## 3. Web & Network Tools

### `fetch_url(url: str)`
Fetches the raw text/HTML content of a web URL using `httpx`.
- **Why it’s essential:** Agents frequently need to read external documentation, API references, or web scrape data. This zero-dependency approach is vastly superior to requiring paid tools like SerpAPI just to read a webpage.

## 4. Context & Environment Tools

### `get_system_info()`
Retrieves OS details, Python version, and current working directory.
- **Why it’s essential:** Agents write different shell commands depending on whether they are running on Windows, Linux, or macOS.

### `get_current_datetime()`
Retrieves the exact UTC timestamp.
- **Why it’s essential:** Required for the agent to correctly timestamp logs, understand chronological data, or author time-sensitive git commits.

## 5. RAG & Human-in-the-loop

### `ask_human(question: str)`
Pauses execution and prompts the user via the CLI terminal.
- **Why it’s essential:** This is the ultimate "escape hatch." If an agent encounters dangerous operations (like `rm -rf`) or ambiguity in the task, it can pause the Swarm and ask the user for explicit clarification.

### `search_vector_memory(query: str, session_id: str, top_k: int = 3)`
Queries the `SwarmVectorMemory` SQLite database using OpenAI embeddings.
- **Why it’s essential:** Provides zero-dependency Retrieval-Augmented Generation (RAG). Instead of starting every session blank, the agent can query past conversations and codebase context to recall previous architecture decisions.
