import os
import json
from pathlib import Path
from unittest import mock
import pytest
import httpx

from aih.agents.tools import (
    read_file,
    write_file,
    list_directory,
    execute_shell,
    execute_python,
    fetch_url,
    get_system_info,
    get_current_datetime,
    ask_human,
    search_vector_memory
)

def test_read_file(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world")
    assert read_file(str(test_file)) == "hello world"
    
def test_read_file_not_found():
    assert "Error:" in read_file("nonexistent.txt")
    
def test_read_file_truncated(tmp_path):
    test_file = tmp_path / "large.txt"
    test_file.write_text("a" * 25000)
    result = read_file(str(test_file))
    assert len(result) < 25000
    assert "truncated" in result

def test_write_file(tmp_path):
    test_file = tmp_path / "nested" / "test.txt"
    result = write_file(str(test_file), "hello world")
    assert "Successfully" in result
    assert test_file.read_text() == "hello world"

def test_write_file_error():
    result = write_file("/root/forbidden.txt", "content")
    assert "Error" in result

def test_list_directory(tmp_path):
    (tmp_path / "file.txt").touch()
    (tmp_path / "folder").mkdir()
    result = list_directory(str(tmp_path))
    assert "file.txt" in result
    assert "folder/" in result

def test_list_directory_not_found():
    assert "Error:" in list_directory("nonexistent_dir")

def test_execute_shell():
    result = execute_shell("echo hello")
    assert "hello" in result

def test_execute_shell_error():
    result = execute_shell("exit 1")
    assert "Command executed successfully" in result # because the command actually runs, but returns exit code 1 with no output
    # Let's test stderr
    result2 = execute_shell("ls /nonexistent_directory_for_test")
    assert "No such file or directory" in result2

def test_execute_shell_timeout():
    result = execute_shell("sleep 3", timeout=1)
    assert "timed out" in result

def test_execute_python():
    result = execute_python("print('hello')")
    assert "hello" in result

def test_execute_python_error():
    result = execute_python("1/0")
    assert "ZeroDivisionError" in result

def test_execute_python_timeout():
    result = execute_python("import time; time.sleep(3)", timeout=1)
    assert "timed out" in result

@mock.patch("httpx.Client.get")
def test_fetch_url(mock_get):
    mock_resp = mock.Mock()
    mock_resp.text = "hello world"
    mock_get.return_value = mock_resp
    result = fetch_url("http://example.com")
    assert result == "hello world"

def test_fetch_url_error():
    assert "Error" in fetch_url("http://localhost:1")

def test_get_system_info():
    result = get_system_info()
    assert "OS:" in result
    assert "Python Version:" in result

def test_get_current_datetime():
    result = get_current_datetime()
    assert "T" in result
    assert "+" in result or "Z" in result or "-" in result

@mock.patch("builtins.input", return_value="user response")
def test_ask_human(mock_input):
    assert ask_human("question") == "user response"

@mock.patch("builtins.input", side_effect=KeyboardInterrupt)
def test_ask_human_interrupt(mock_input):
    assert ask_human("question") == "Human aborted or disconnected."

@mock.patch("aih.agents.orchestrator.SwarmVectorMemory")
def test_search_vector_memory(mock_memory, tmp_path):
    mock_instance = mock.Mock()
    mock_instance.search_knowledge.return_value = ["context 1", "context 2"]
    mock_memory.return_value = mock_instance
    
    with mock.patch("os.environ.get", return_value="dummy_key"):
        with mock.patch("pathlib.Path.exists", return_value=True):
            result = search_vector_memory("query", "sess_id")
            assert "context 1" in result
            assert "context 2" in result

@mock.patch("pathlib.Path.exists", return_value=False)
def test_search_vector_memory_no_db(mock_exists):
    assert "empty or uninitialized" in search_vector_memory("query", "sess_id")

@mock.patch("pathlib.Path.exists", return_value=True)
def test_search_vector_memory_no_api_key(mock_exists):
    with mock.patch("os.environ.get", return_value=""):
        assert "AIH_AGENT_API_KEY required" in search_vector_memory("query", "sess_id")

@mock.patch("aih.agents.orchestrator.SwarmVectorMemory")
def test_search_vector_memory_no_results(mock_memory):
    mock_instance = mock.Mock()
    mock_instance.search_knowledge.return_value = []
    mock_memory.return_value = mock_instance
    
    with mock.patch("os.environ.get", return_value="dummy_key"):
        with mock.patch("pathlib.Path.exists", return_value=True):
            assert "No relevant context" in search_vector_memory("query", "sess_id")
