"""Intelligent routing module for AI-Harness.

This module provides a stub implementation that forwards to the legacy
keyword classifier but is structured so that a real LLM call can replace
the body without affecting callers.
"""

from __future__ import annotations

try:
    from pydantic import BaseModel, Field
except ImportError:
    BaseModel = object  # type: ignore
    Field = lambda **kwargs: None  # type: ignore

from aih.config import load_config


class RouterResponse(BaseModel):
    """Explicit contract for the LLM routing decision.
    
    This enforces structured outputs from any model integrated in the future.
    """
    mode: str = Field(..., description="The calculated execution mode (e.g., 'ask', 'do', 'deep')")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Confidence score of the routing decision")
    reasoning: str = Field("", description="Optional explanation for the route selection")

def intelligent_route(request: str) -> str:
    """Determine the routing *mode* for *request*.

    The function first checks ``router_model`` in the configuration. If a
    concrete model is configured, it would call the appropriate LLM API
    (OpenAI, Anthropic, etc.). For now we keep a stub that simply forwards
    to :func:`classify_mode`.
    """
    cfg = load_config()
    model = cfg.router_model
    
    # Lazy import to avoid circular dependency with routing module
    from aih.routing import classify_mode  # noqa: PLC0415
    
    if model == "stub":
        return classify_mode(request)
        
    import os
    import sys
    import json
    import time
    from aih.display import color
    
    try:
        import httpx
    except ImportError:
        print(color("Warning: httpx not installed. Falling back to heuristic routing.", "yellow", stream=sys.stderr), file=sys.stderr)
        return classify_mode(request)
    
    api_key = os.environ.get("AIH_AGENT_API_KEY")
    if not api_key:
        print(color("Warning: AIH_AGENT_API_KEY not set. Falling back to heuristic routing.", "yellow", stream=sys.stderr), file=sys.stderr)
        return classify_mode(request)
        
    base_url = os.environ.get("AIH_OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a routing agent. Respond with JSON matching the RouterResponse schema. Determine if the request requires 'ask' (question), 'do' (action), or 'deep' (comprehensive)."},
            {"role": "user", "content": request}
        ],
        "response_format": {"type": "json_object"}
    }
    
    # Retry loop with exponential backoff
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(f"{base_url}/chat/completions", json=payload, headers=headers)
                response.raise_for_status()
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                mode = parsed.get("mode", "")
                if mode in ("ask", "do", "deep", "prompt", "compile"):
                    return mode
                return classify_mode(request)
                
        except httpx.HTTPStatusError as e:
            # Handle rate limits specifically
            if e.response.status_code == 429 and attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            print(color(f"Warning: LLM routing HTTP error ({e}). Falling back.", "yellow", stream=sys.stderr), file=sys.stderr)
            return classify_mode(request)
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            print(color(f"Warning: LLM routing failed ({e}). Falling back.", "yellow", stream=sys.stderr), file=sys.stderr)
            return classify_mode(request)
            
    return classify_mode(request)

