"""Core tools for AI-Harness Agents.

These tools provide the foundational capabilities for agents to interact with
the host system, search the web, execute code, and ask for human assistance.
"""

import os
import sys
import subprocess
import datetime
import platform
import httpx
from pathlib import Path
from typing import Any, List, Optional
from aih.display import color


def read_file(filepath: str) -> str:
    """Reads the contents of a local file.
    
    Args:
        filepath: The path to the file to read.
        
    Returns:
        The text content of the file, or an error message if it cannot be read.
    """
    try:
        path = Path(filepath)
        if not path.is_file():
            return f"Error: '{filepath}' is not a valid file."
        # Read up to a reasonable limit to prevent context explosion
        content = path.read_text(encoding="utf-8", errors="replace")
        if len(content) > 20000:
            return content[:20000] + f"\n... [File truncated, total length: {len(content)} chars]"
        return content
    except Exception as e:
        return f"Error reading file '{filepath}': {e}"


def write_file(filepath: str, content: str) -> str:
    """Writes text content to a local file, creating parent directories if needed.
    
    Args:
        filepath: The path where the file should be saved.
        content: The text content to write.
        
    Returns:
        A success message or an error message.
    """
    try:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Successfully wrote {len(content)} characters to '{filepath}'."
    except Exception as e:
        return f"Error writing file '{filepath}': {e}"


def list_directory(path: str = ".") -> str:
    """Lists the files and folders in a given directory.
    
    Args:
        path: The directory path to list. Defaults to current directory.
        
    Returns:
        A formatted list of items in the directory, or an error message.
    """
    try:
        p = Path(path)
        if not p.is_dir():
            return f"Error: '{path}' is not a valid directory."
        
        items = []
        for item in p.iterdir():
            suffix = "/" if item.is_dir() else ""
            items.append(f"{item.name}{suffix}")
            
        items.sort()
        return "\n".join(items) if items else "(Empty directory)"
    except Exception as e:
        return f"Error listing directory '{path}': {e}"


def execute_shell(command: str, timeout: int = 30) -> str:
    """Executes a terminal shell command.
    
    Args:
        command: The shell command to execute.
        timeout: Maximum seconds to allow the command to run.
        
    Returns:
        The combined stdout/stderr of the command execution, or an error message.
    """
    try:
        print(color(f"Running command: {command}", "yellow"))
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]:\n{result.stderr}"
        if not output.strip():
            output = f"Command executed successfully (exit code {result.returncode}) with no output."
        return output
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds."
    except Exception as e:
        return f"Error executing command: {e}"


def execute_python(code: str, timeout: int = 30) -> str:
    """Executes python code in a standalone subprocess and returns the output.
    
    Args:
        code: The python script to execute.
        timeout: Maximum seconds to allow the script to run.
        
    Returns:
        The stdout/stderr of the script, or an error message.
    """
    try:
        print(color("Running Python snippet...", "yellow"))
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]:\n{result.stderr}"
        if not output.strip():
            output = f"Python executed successfully (exit code {result.returncode}) with no output."
        return output
    except subprocess.TimeoutExpired:
        return f"Error: Python execution timed out after {timeout} seconds."
    except Exception as e:
        return f"Error executing python: {e}"


def fetch_url(url: str) -> str:
    """Fetches the text content of a web URL.
    
    Args:
        url: The HTTP/HTTPS URL to fetch.
        
    Returns:
        The text content of the response, or an error message.
    """
    try:
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()
            text = resp.text
            if len(text) > 20000:
                text = text[:20000] + f"\n... [Response truncated, total length: {len(text)} chars]"
            return text
    except Exception as e:
        return f"Error fetching URL '{url}': {e}"


def get_system_info() -> str:
    """Retrieves basic information about the host system environment.
    
    Returns:
        A string containing OS, Python version, and working directory.
    """
    info = [
        f"OS: {platform.system()} {platform.release()} ({platform.machine()})",
        f"Python Version: {platform.python_version()}",
        f"Working Directory: {os.getcwd()}"
    ]
    return "\n".join(info)


def get_current_datetime() -> str:
    """Retrieves the current date and time.
    
    Returns:
        The current ISO 8601 formatted datetime string.
    """
    return datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat()


def ask_human(question: str) -> str:
    """Pauses execution and asks the human user a question via the CLI.
    
    Args:
        question: The question to display to the user.
        
    Returns:
        The human's response.
    """
    print(color(f"\n[Agent Question]: {question}", "magenta"))
    try:
        return input(color("Your response: ", "cyan"))
    except (EOFError, KeyboardInterrupt):
        return "Human aborted or disconnected."


def search_vector_memory(query: str, session_id: str, top_k: int = 3) -> str:
    """Searches the agent's vector memory for relevant past context.
    
    Args:
        query: The semantic search query.
        session_id: The current session ID to scope the search.
        top_k: Number of results to return.
        
    Returns:
        The concatenated semantic search results.
    """
    try:
        from aih.agents.orchestrator import SwarmVectorMemory
        import sqlite3
        
        # We need a db_path that matches the actual orchestrator's path.
        # Since tools are usually stateless, we instantiate a temp connection to the default path.
        db_path = Path.home() / ".config" / "ai-harness" / "memory.db"
        if not db_path.exists():
            return "Vector memory is empty or uninitialized."
            
        api_key = os.environ.get("AIH_AGENT_API_KEY", "")
        if not api_key:
            return "Error: AIH_AGENT_API_KEY required for vector search."
            
        memory = SwarmVectorMemory(api_key=api_key, db_path=db_path)
        results = memory.search_knowledge(session_id, query, top_k)
        
        if not results:
            return "No relevant context found in vector memory."
            
        return "\n\n--- Result ---\n\n".join(results)
    except Exception as e:
        return f"Error searching vector memory: {e}"

def get_standard_tools() -> List[Any]:
    """Returns the default suite of 10 autonomous agent tools."""
    return [
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
    ]
