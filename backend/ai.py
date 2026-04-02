import os
import httpx
from typing import Optional


def load_openrouter_key() -> str:
    """
    Load OpenRouter API key from environment.
    
    Returns:
        str: API key
        
    Raises:
        ValueError: If OPENROUTER_API_KEY not found in environment
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in environment")
    return api_key


def call_openrouter(prompt: str, model: str = "openai/gpt-oss-120b") -> str:
    """
    Call OpenRouter API with a prompt.
    
    Args:
        prompt: User prompt to send to AI
        model: Model identifier (default: openai/gpt-oss-120b)
        
    Returns:
        str: AI response text
        
    Raises:
        ValueError: If API key is missing
        httpx.TimeoutException: If request times out
        httpx.HTTPError: If API returns error
    """
    api_key = load_openrouter_key()
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Kanban Studio"
    }
    
    body = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, headers=headers, json=body)
        response.raise_for_status()
        
        data = response.json()
        return data["choices"][0]["message"]["content"]



def call_openrouter_structured(
    system_prompt: str,
    user_message: str,
    conversation_history: list = None,
    model: str = "openai/gpt-oss-120b"
) -> dict:
    """
    Call OpenRouter API with structured output for board manipulation.
    
    Args:
        system_prompt: System prompt with board state and instructions
        user_message: User's message
        conversation_history: Previous messages in conversation
        model: Model identifier
        
    Returns:
        dict: Parsed JSON response with 'response' and optional 'board_update'
        
    Raises:
        ValueError: If API key is missing
        httpx.TimeoutException: If request times out
        httpx.HTTPError: If API returns error
    """
    api_key = load_openrouter_key()
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Kanban Studio"
    }
    
    # Build messages array
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add conversation history if provided
    if conversation_history:
        messages.extend(conversation_history)
    
    # Add current user message
    messages.append({"role": "user", "content": user_message})
    
    body = {
        "model": model,
        "messages": messages,
        "response_format": {"type": "json_object"}
    }
    
    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, headers=headers, json=body)
        response.raise_for_status()
        
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        
        # Parse JSON response
        import json
        return json.loads(content)
