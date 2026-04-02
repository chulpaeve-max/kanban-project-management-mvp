import json
from typing import Dict, Any


def get_system_prompt(board_data: Dict[str, Any]) -> str:
    """
    Generate system prompt for AI with current board state.
    
    Args:
        board_data: Current board state with columns and cards
        
    Returns:
        System prompt string
    """
    board_json = json.dumps(board_data, indent=2)
    
    return f"""You are an AI assistant for a Kanban board application. You can help users manage their board by creating, updating, moving, and deleting cards.

Current Board State:
{board_json}

You can respond in two ways:
1. Text-only response (for questions, explanations, etc.)
2. Text response with board updates (for actions like creating/moving cards)

When the user asks you to modify the board, respond with:
- A natural language response explaining what you did
- A board_update object with the changes

Board Update Format:
{{
  "response": "Your natural language response",
  "board_update": {{
    "cards": [
      {{
        "action": "create",
        "column_id": <column_id>,
        "title": "Card title",
        "details": "Card details",
        "position": <position>
      }},
      {{
        "action": "move",
        "id": <card_id>,
        "column_id": <target_column_id>,
        "position": <position>
      }},
      {{
        "action": "update",
        "id": <card_id>,
        "title": "New title",
        "details": "New details"
      }},
      {{
        "action": "delete",
        "id": <card_id>
      }}
    ]
  }}
}}

Rules:
- Always provide a helpful response text
- Only include board_update if the user asks to modify the board
- Use exact column IDs and card IDs from the current board state
- For "create" action: provide column_id, title, details (optional), position
- For "move" action: provide id, column_id, position
- For "update" action: provide id, and fields to update (title, details)
- For "delete" action: provide id only
- Position is 0-indexed (0 = first card in column)
- Be concise and helpful
"""


def format_conversation_history(messages: list) -> list:
    """
    Format conversation history for AI API.
    
    Args:
        messages: List of message dicts with role and content
        
    Returns:
        Formatted messages list
    """
    return [{"role": msg["role"], "content": msg["content"]} for msg in messages]
