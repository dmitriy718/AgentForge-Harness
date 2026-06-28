import sqlite3
import json
from pathlib import Path
from unittest import mock
import pytest

from aih.agents.orchestrator import SwarmMemory, ContextCompressor, SwarmAgent, SwarmOrchestrator


@pytest.fixture
def memory_db(tmp_path: Path):
    db_path = tmp_path / "memory.db"
    return SwarmMemory(db_path=db_path)


def test_swarm_memory_append_and_get(memory_db):
    memory_db.append_message("session_1", "user", "hello")
    memory_db.append_message("session_1", "assistant", "world")
    
    history = memory_db.get_history("session_1")
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "hello"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "world"

def test_swarm_memory_prune(memory_db):
    for i in range(15):
        memory_db.append_message("session_2", "user", f"msg {i}")
        
    # Prune keeping only the latest 5 messages
    deleted = memory_db.prune_history("session_2", keep_latest=5)
    assert deleted == 10
    
    # Verify the remaining are the last 5
    history = memory_db.get_history("session_2", limit=100)
    assert len(history) == 5
    assert history[0]["content"] == "msg 10"
    assert history[-1]["content"] == "msg 14"


def test_context_compressor():
    compressor = ContextCompressor(max_tokens=10, model="gpt-4")
    # Mocking count_tokens so we don't strictly depend on tiktoken implementation details
    compressor.count_tokens = lambda text: len(text.split())
    
    messages = [
        {"role": "system", "content": "system prompt 1 2 3"},
        {"role": "user", "content": "user prompt 4 5 6"},
        {"role": "assistant", "content": "assistant reply 7 8 9"},
    ]
    # system=4, user=4, assistant=4 -> total=12. Max=10.
    # It should evict user prompt.
    compressed = compressor.compress(messages)
    assert len(compressed) == 2
    assert compressed[0]["role"] == "system"
    assert compressed[1]["role"] == "assistant"


def test_swarm_orchestrator_tool_execution():
    def mock_tool(x: int) -> int:
        """Returns x + 1"""
        if x < 0:
            raise ValueError("Negative")
        return x + 1

    agent = SwarmAgent(name="Math", system_prompt="You do math", tools=[mock_tool])
    orchestrator = SwarmOrchestrator(api_key="test")
    
    # Test success
    tool_call = {
        "id": "call_1",
        "function": {
            "name": "mock_tool",
            "arguments": '{"x": 5}'
        }
    }
    res = orchestrator._execute_tool(tool_call, agent)
    data = json.loads(res)
    assert data["status"] == "success"
    assert data["result"] == 6

    # Test tool error
    tool_call_err = {
        "function": {
            "name": "mock_tool",
            "arguments": '{"x": -1}'
        }
    }
    res2 = orchestrator._execute_tool(tool_call_err, agent)
    data2 = json.loads(res2)
    assert data2["status"] == "error"
    assert "Negative" in data2["error"]

    # Test unknown tool
    tool_call_unk = {
        "function": {
            "name": "unknown_tool",
            "arguments": '{}'
        }
    }
    res3 = orchestrator._execute_tool(tool_call_unk, agent)
    data3 = json.loads(res3)
    assert data3["status"] == "error"
    assert "not found" in data3["error"]


def test_swarm_orchestrator_run_agent(memory_db):
    agent = SwarmAgent(name="Test", system_prompt="You are a test agent")
    orchestrator = SwarmOrchestrator(api_key="test")
    orchestrator.memory = memory_db
    
    # Mock httpx.Client.post
    mock_response = mock.MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"role": "assistant", "content": "mocked response"}}]
    }
    
    with mock.patch("httpx.Client.post", return_value=mock_response):
        result = orchestrator.run_agent(agent, "session_1", "hello")
        
    assert result == "mocked response"
    history = memory_db.get_history("session_1")
    assert history[-1]["content"] == "mocked response"


def test_swarm_orchestrator_run_agent_with_tool(memory_db):
    def mock_tool(x: int) -> int: return x + 1
    agent = SwarmAgent(name="Test", system_prompt="Test", tools=[mock_tool])
    orchestrator = SwarmOrchestrator(api_key="test")
    orchestrator.memory = memory_db
    
    # First response: tool call. Second response: final answer.
    resp1 = mock.MagicMock()
    resp1.json.return_value = {
        "choices": [{"message": {
            "role": "assistant",
            "content": None,
            "tool_calls": [{"id": "call_1", "function": {"name": "mock_tool", "arguments": '{"x": 5}'}}]
        }}]
    }
    resp2 = mock.MagicMock()
    resp2.json.return_value = {
        "choices": [{"message": {"role": "assistant", "content": "tool done"}}]
    }
    
    with mock.patch("httpx.Client.post", side_effect=[resp1, resp2]):
        result = orchestrator.run_agent(agent, "session_2", "run tool")
        
    assert result == "tool done"


def test_swarm_vector_memory(memory_db):
    from aih.agents.orchestrator import SwarmVectorMemory
    
    with mock.patch.object(SwarmVectorMemory, "_get_embedding") as mock_embed:
        # Mock embeddings to be simple vectors
        # "python script" -> [1.0, 0.0]
        # "bash script" -> [0.0, 1.0]
        # query "python" -> [0.9, 0.1]
        
        def _mock_emb(text):
            if "python" in text and "script" in text: return [1.0, 0.0]
            if "bash" in text: return [0.0, 1.0]
            return [0.9, 0.1] # query
            
        mock_embed.side_effect = _mock_emb
        
        v_memory = SwarmVectorMemory(api_key="test", db_path=Path(memory_db.conn.execute("PRAGMA database_list").fetchall()[0][2]))
        v_memory.add_knowledge("sess_3", "This is a python script")
        v_memory.add_knowledge("sess_3", "This is a bash script")
        
        results = v_memory.search_knowledge("sess_3", "query python", top_k=1)
        
        assert len(results) == 1
        assert "python script" in results[0]

