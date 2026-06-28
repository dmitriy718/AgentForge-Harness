# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - Production Swarm Release
### Added
- **Multi-Agent Swarm Orchestrator**: Replaced linear synchronous execution with a highly dynamic, self-correcting `SwarmOrchestrator`.
- **Zero-Dependency RAG**: Integrated `SwarmVectorMemory`, allowing agents to semantically search conversation history and repository context using native SQLite + OpenAI Embeddings.
- **Agent Tools Suite**: Added 10 core tools for complete autonomy (Python execution, File I/O, Web Scraper, Shell execution, Vector Search, Human-in-the-loop escapes, etc.).
- **Dockerized CI/CD**: Added complete Docker and Github Actions pipelines testing against Python 3.10-3.13.

### Changed
- **Network Resiliency**: Replaced `urllib` with asynchronous `httpx`.
- **Rate-Limit Tolerance**: Integrated `tenacity` for flawless exponential backoff when encountering OpenAI 429 limits.
- **Dependency Base**: Updated `pyproject.toml` with `pydantic`, `tiktoken`, `tenacity`, and `httpx`.

### Fixed
- Fixed unbounded memory growth by implementing sliding-window pruning in SQLite task state.
- Fixed `get_history` SQL query bug to fetch the latest context correctly.
- Re-architected system prompts to prevent JSON parsing faults (now using `response_format={"type": "json_object"}`).
