import pytest
from unittest.mock import patch, MagicMock
import httpx
import ai


def test_load_openrouter_key_success():
    """Test loading API key from environment."""
    with patch('os.getenv') as mock_getenv:
        mock_getenv.return_value = "test-api-key"
        result = ai.load_openrouter_key()
        assert result == "test-api-key"
        mock_getenv.assert_called_once_with("OPENROUTER_API_KEY")


def test_load_openrouter_key_missing():
    """Test error when API key is missing."""
    with patch('os.getenv') as mock_getenv:
        mock_getenv.return_value = None
        with pytest.raises(ValueError, match="OPENROUTER_API_KEY not found"):
            ai.load_openrouter_key()


def test_call_openrouter_success():
    """Test successful API call."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "The answer is 4"
                }
            }
        ]
    }
    
    with patch('os.getenv') as mock_getenv, \
         patch('httpx.Client') as mock_client:
        
        mock_getenv.return_value = "test-api-key"
        mock_client_instance = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        mock_client_instance.post.return_value = mock_response
        
        result = ai.call_openrouter("2+2")
        
        assert result == "The answer is 4"
        
        # Verify request was made correctly
        mock_client_instance.post.assert_called_once()
        call_args = mock_client_instance.post.call_args
        
        assert call_args[0][0] == "https://openrouter.ai/api/v1/chat/completions"
        assert call_args[1]["headers"]["Authorization"] == "Bearer test-api-key"
        assert call_args[1]["headers"]["Content-Type"] == "application/json"
        assert call_args[1]["json"]["model"] == "openai/gpt-oss-120b"
        assert call_args[1]["json"]["messages"][0]["content"] == "2+2"


def test_call_openrouter_timeout():
    """Test timeout handling."""
    with patch('os.getenv') as mock_getenv, \
         patch('httpx.Client') as mock_client:
        
        mock_getenv.return_value = "test-api-key"
        mock_client_instance = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        mock_client_instance.post.side_effect = httpx.TimeoutException("Timeout")
        
        with pytest.raises(httpx.TimeoutException):
            ai.call_openrouter("test prompt")


def test_call_openrouter_http_error():
    """Test HTTP error handling."""
    with patch('os.getenv') as mock_getenv, \
         patch('httpx.Client') as mock_client:
        
        mock_getenv.return_value = "test-api-key"
        mock_client_instance = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Error", request=MagicMock(), response=MagicMock()
        )
        mock_client_instance.post.return_value = mock_response
        
        with pytest.raises(httpx.HTTPStatusError):
            ai.call_openrouter("test prompt")


def test_call_openrouter_custom_model():
    """Test calling with custom model."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "response"}}]
    }
    
    with patch('os.getenv') as mock_getenv, \
         patch('httpx.Client') as mock_client:
        
        mock_getenv.return_value = "test-api-key"
        mock_client_instance = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        mock_client_instance.post.return_value = mock_response
        
        ai.call_openrouter("test", model="custom-model")
        
        call_args = mock_client_instance.post.call_args
        assert call_args[1]["json"]["model"] == "custom-model"



def test_call_openrouter_structured_success():
    """Test successful structured API call."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": '{"response": "Created card", "board_update": {"cards": [{"action": "create", "title": "Test"}]}}'
                }
            }
        ]
    }
    
    with patch('os.getenv') as mock_getenv, \
         patch('httpx.Client') as mock_client:
        
        mock_getenv.return_value = "test-api-key"
        mock_client_instance = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        mock_client_instance.post.return_value = mock_response
        
        result = ai.call_openrouter_structured(
            system_prompt="System prompt",
            user_message="Create a card",
            conversation_history=[]
        )
        
        assert result["response"] == "Created card"
        assert "board_update" in result
        assert result["board_update"]["cards"][0]["action"] == "create"


def test_call_openrouter_structured_with_history():
    """Test structured call with conversation history."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": '{"response": "Done"}'}}]
    }
    
    history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi"}
    ]
    
    with patch('os.getenv') as mock_getenv, \
         patch('httpx.Client') as mock_client:
        
        mock_getenv.return_value = "test-api-key"
        mock_client_instance = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        mock_client_instance.post.return_value = mock_response
        
        ai.call_openrouter_structured(
            system_prompt="System",
            user_message="Test",
            conversation_history=history
        )
        
        call_args = mock_client_instance.post.call_args
        messages = call_args[1]["json"]["messages"]
        
        # Should have system + history + user message
        assert len(messages) == 4
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "Hello"
        assert messages[2]["role"] == "assistant"
        assert messages[3]["role"] == "user"
        assert messages[3]["content"] == "Test"


def test_call_openrouter_structured_json_format():
    """Test that structured call requests JSON format."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": '{"response": "OK"}'}}]
    }
    
    with patch('os.getenv') as mock_getenv, \
         patch('httpx.Client') as mock_client:
        
        mock_getenv.return_value = "test-api-key"
        mock_client_instance = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        mock_client_instance.post.return_value = mock_response
        
        ai.call_openrouter_structured(
            system_prompt="System",
            user_message="Test"
        )
        
        call_args = mock_client_instance.post.call_args
        assert call_args[1]["json"]["response_format"] == {"type": "json_object"}
