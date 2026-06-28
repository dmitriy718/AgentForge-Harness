"""Multi-agent orchestration system for AI-Harness.

Provides memory retrieval, tool selection, context compression, error recovery,
and task state tracking for advanced AI execution loops.
"""

from __future__ import annotations

import json
import sqlite3
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import httpx

try:
    import tiktoken
except ImportError:
    tiktoken = None  # type: ignore

from aih.display import color


# ---------------------------------------------------------------------------
# Long-Term Memory (SQLite)
# ---------------------------------------------------------------------------

class SwarmMemory:
    """Persistent task state and conversation memory."""

    def __init__(self, db_path: Path | None = None) -> None:
        if db_path is None:
            db_path = Path.home() / ".config" / "ai-harness" / "memory.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS conversation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def append_message(self, session_id: str, role: str, content: str) -> None:
        self.conn.execute(
            "INSERT INTO conversation (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content)
        )
        self.conn.commit()

    def get_history(self, session_id: str, limit: int = 50) -> List[Dict[str, str]]:
        cursor = self.conn.execute(
            "SELECT role, content FROM conversation WHERE session_id = ? ORDER BY id ASC LIMIT ?",
            (session_id, limit)
        )
        return [{"role": row["role"], "content": row["content"]} for row in cursor]

    def prune_history(self, session_id: str, keep_latest: int = 100) -> int:
        """Deletes older messages, keeping only the N most recent to prevent unbounded growth."""
        cursor = self.conn.execute(
            "SELECT id FROM conversation WHERE session_id = ? ORDER BY id DESC LIMIT 1 OFFSET ?",
            (session_id, keep_latest - 1)
        )
        row = cursor.fetchone()
        if not row:
            return 0
            
        threshold_id = row["id"]
        cursor = self.conn.execute(
            "DELETE FROM conversation WHERE session_id = ? AND id < ?",
            (session_id, threshold_id)
        )
        self.conn.commit()
        return cursor.rowcount


# ---------------------------------------------------------------------------
# Context Compression
# ---------------------------------------------------------------------------

class ContextCompressor:
    """Manages token limits and sliding window context."""

    def __init__(self, max_tokens: int = 8000, model: str = "gpt-4") -> None:
        self.max_tokens = max_tokens
        self.model = model
        self.encoding = None
        if tiktoken:
            try:
                self.encoding = tiktoken.encoding_for_model(model)
            except KeyError:
                self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        if self.encoding:
            return len(self.encoding.encode(text))
        # Fallback heuristic: 1 token ~= 4 chars
        return len(text) // 4

    def compress(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Evict oldest non-system messages until under budget."""
        total_tokens = sum(self.count_tokens(m.get("content", "") or "") for m in messages)
        
        if total_tokens <= self.max_tokens:
            return messages

        compressed = [m for m in messages if m.get("role") == "system"]
        mutable_history = [m for m in messages if m.get("role") != "system"]
        
        while mutable_history and total_tokens > self.max_tokens:
            removed = mutable_history.pop(0)
            total_tokens -= self.count_tokens(removed.get("content", "") or "")
            
        return compressed + mutable_history


# ---------------------------------------------------------------------------
# Tools and Agent Definitions
# ---------------------------------------------------------------------------

@dataclass
class SwarmAgent:
    """A specialized agent persona."""
    name: str
    system_prompt: str
    tools: List[Callable[..., Any]] = field(default_factory=list)
    model: str = "gpt-4-turbo"


class SwarmOrchestrator:
    """Multi-agent evaluation and execution loop with tool support."""

    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1") -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.memory = SwarmMemory()
        self.client = httpx.Client(timeout=60.0)

    def _execute_tool(self, tool_call: Dict[str, Any], agent: SwarmAgent) -> str:
        """Execute a requested tool and return JSON string result."""
        name = tool_call["function"]["name"]
        args = json.loads(tool_call["function"]["arguments"])
        
        for tool in agent.tools:
            if tool.__name__ == name:
                try:
                    result = tool(**args)
                    return json.dumps({"status": "success", "result": result})
                except Exception as e:
                    return json.dumps({"status": "error", "error": str(e)})
                    
        return json.dumps({"status": "error", "error": f"Tool {name} not found"})

    def run_agent(self, agent: SwarmAgent, session_id: str, prompt: str) -> str:
        """Run a resilient evaluation loop for a specific agent."""
        self.memory.append_message(session_id, "user", prompt)
        
        messages = [{"role": "system", "content": agent.system_prompt}]
        messages.extend(self.memory.get_history(session_id))
        
        compressor = ContextCompressor(model=agent.model)
        
        # Format tools for OpenAI API
        tools_payload = []
        for tool in agent.tools:
            # Minimal extraction (in production, use Pydantic signature inspection)
            tools_payload.append({
                "type": "function",
                "function": {
                    "name": tool.__name__,
                    "description": tool.__doc__ or "Execute a tool",
                    "parameters": {"type": "object", "properties": {}}
                }
            })

        max_iterations = 5
        
        for iteration in range(max_iterations):
            messages = compressor.compress(messages)
            
            payload: Dict[str, Any] = {
                "model": agent.model,
                "messages": messages
            }
            if tools_payload:
                payload["tools"] = tools_payload
                
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            try:
                response = self.client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                choice = data["choices"][0]["message"]
                
                messages.append(choice)
                
                if "tool_calls" in choice and choice["tool_calls"]:
                    for tool_call in choice["tool_calls"]:
                        print(color(f"[{agent.name}] Executing tool: {tool_call['function']['name']}", "cyan"))
                        tool_result = self._execute_tool(tool_call, agent)
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": tool_result
                        })
                    continue  # Loop back to let the LLM process the tool result
                    
                # No tool calls, final answer
                content = choice.get("content") or ""
                self.memory.append_message(session_id, "assistant", content)
                return content
                
            except httpx.HTTPStatusError as e:
                # Self-correction on rate limit or temp error
                if e.response.status_code == 429:
                    time.sleep(2)
                    continue
                return f"Error: {e.response.text}"
            except Exception as e:
                return f"Critical Error: {str(e)}"
                
        return "Error: Maximum iteration limit reached without final answer."
