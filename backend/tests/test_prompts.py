import pytest
from prompts import get_system_prompt, format_conversation_history


def test_system_prompt_includes_board():
    """Test that system prompt includes board data."""
    board_data = {
        "id": 1,
        "title": "Test Board",
        "columns": [
            {
                "id": 1,
                "title": "Todo",
                "position": 0,
                "cards": [
                    {"id": 1, "title": "Task 1", "details": "Details", "position": 0}
                ]
            }
        ]
    }
    
    prompt = get_system_prompt(board_data)
    
    assert "Test Board" in prompt
    assert "Todo" in prompt
    assert "Task 1" in prompt
    assert "board_update" in prompt


def test_system_prompt_format():
    """Test that system prompt has correct format."""
    board_data = {
        "id": 1,
        "title": "Board",
        "columns": []
    }
    
    prompt = get_system_prompt(board_data)
    
    assert "Kanban board" in prompt
    assert "create" in prompt
    assert "move" in prompt
    assert "update" in prompt
    assert "delete" in prompt
    assert "action" in prompt


def test_format_conversation_history():
    """Test conversation history formatting."""
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there"}
    ]
    
    formatted = format_conversation_history(messages)
    
    assert len(formatted) == 2
    assert formatted[0]["role"] == "user"
    assert formatted[0]["content"] == "Hello"
    assert formatted[1]["role"] == "assistant"
    assert formatted[1]["content"] == "Hi there"


def test_format_empty_history():
    """Test formatting empty conversation history."""
    formatted = format_conversation_history([])
    assert formatted == []
