# AI Connectivity - Design

## Architecture Overview

Simple integration with OpenRouter API for basic AI connectivity testing. The design follows a straightforward request-response pattern with proper error handling.

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Client    │─────▶│  FastAPI     │─────▶│ OpenRouter  │
│  (curl/test)│      │  /api/ai/test│      │     API     │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │   backend/   │
                     │    ai.py     │
                     └──────────────┘
```

## Component Design

### 1. backend/ai.py

New module for AI integration logic.

**Functions:**

```python
def load_openrouter_key() -> str:
    """
    Load OpenRouter API key from environment.
    
    Returns:
        str: API key
        
    Raises:
        ValueError: If OPENROUTER_API_KEY not found in environment
    """
    
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
```

**Implementation Details:**
- Use httpx.Client for HTTP requests
- Timeout: 30 seconds
- Headers:
  - Authorization: Bearer {api_key}
  - Content-Type: application/json
  - HTTP-Referer: http://localhost:8000
  - X-Title: Kanban Studio
- Request body format:
  ```json
  {
    "model": "openai/gpt-oss-120b",
    "messages": [
      {"role": "user", "content": "{prompt}"}
    ]
  }
  ```
- Extract response from: response.json()["choices"][0]["message"]["content"]

### 2. backend/main.py Updates

**New Endpoint:**

```python
@app.post("/api/ai/test")
async def test_ai(
    request: TestAIRequest,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Test endpoint for AI connectivity.
    
    Requires authentication.
    Accepts prompt, returns AI response.
    """
```

**Request Schema:**
```python
class TestAIRequest(BaseModel):
    prompt: str
```

**Response Schema:**
```python
class TestAIResponse(BaseModel):
    response: str
```

**Error Handling:**
- 401: Not authenticated
- 500: AI service error (with message)
- 503: AI service unavailable

### 3. backend/schemas.py Updates

Add new Pydantic models:
- TestAIRequest
- TestAIResponse

## Error Handling Strategy

### Missing API Key
- Check on application startup
- Return clear error message
- Log warning (without exposing key)

### Network Errors
- Catch httpx.TimeoutException
- Catch httpx.HTTPError
- Return 503 with user-friendly message
- Log full error for debugging

### API Errors
- Parse error response from OpenRouter
- Return 500 with sanitized message
- Log full error details

## Testing Strategy

### Unit Tests (backend/tests/test_ai.py)

**test_load_openrouter_key:**
- Mock os.getenv
- Test success case
- Test missing key case

**test_call_openrouter_success:**
- Mock httpx.post
- Verify request format
- Verify response parsing

**test_call_openrouter_timeout:**
- Mock httpx.post to raise TimeoutException
- Verify exception is raised

**test_call_openrouter_api_error:**
- Mock httpx.post to return error response
- Verify exception is raised

### Integration Tests (backend/tests/test_main.py)

**test_ai_test_endpoint_authenticated:**
- Mock ai.call_openrouter
- Send valid request
- Verify response format

**test_ai_test_endpoint_unauthenticated:**
- Send request without auth token
- Verify 401 response

**test_ai_test_endpoint_ai_failure:**
- Mock ai.call_openrouter to raise exception
- Verify error handling

### Manual Testing

```bash
# 1. Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"password"}'

# 2. Test AI (use token from step 1)
curl -X POST http://localhost:8000/api/ai/test \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{"prompt":"2+2"}'

# Expected response:
# {"response":"4"} or similar
```

## Security Considerations

1. API key never logged or exposed in errors
2. All endpoints require authentication
3. Rate limiting handled by OpenRouter
4. No sensitive data in AI prompts (for this phase)

## Performance Considerations

1. 30-second timeout prevents hanging requests
2. No caching (simple implementation)
3. Synchronous calls (async in future if needed)

## Dependencies

Existing in requirements.txt:
- httpx (already installed)
- python-dotenv (already installed)

No new dependencies needed.

## Deployment Notes

1. Ensure OPENROUTER_API_KEY in .env file
2. Rebuild Docker container
3. Verify API key is loaded on startup
4. Test endpoint with curl

## Future Enhancements (Out of Scope)

- Structured outputs (Part 9)
- Conversation history (Part 9)
- Streaming responses
- Response caching
- Multiple model support
- Retry logic with exponential backoff
