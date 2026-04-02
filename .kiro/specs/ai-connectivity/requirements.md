# AI Connectivity - Requirements

## Overview
Enable basic connectivity to OpenRouter AI service to verify API integration works before implementing structured outputs and board manipulation features.

## User Stories

### US-1: API Key Configuration
As a developer, I need to configure the OpenRouter API key so that the application can authenticate with the AI service.

Acceptance Criteria:
- API key is read from .env file
- Application fails gracefully if API key is missing
- API key is not exposed in logs or error messages

### US-2: Basic AI Test Endpoint
As a developer, I need a test endpoint to verify AI connectivity so that I can confirm the integration works before building complex features.

Acceptance Criteria:
- POST /api/ai/test endpoint exists
- Endpoint requires authentication
- Endpoint accepts JSON: {"prompt": "string"}
- Endpoint returns JSON: {"response": "string"}
- Simple prompts like "2+2" return reasonable responses
- Unauthenticated requests return 401

### US-3: Error Handling
As a developer, I need proper error handling for AI failures so that the application remains stable when the AI service is unavailable.

Acceptance Criteria:
- Missing API key returns clear error message
- Network failures are caught and logged
- API rate limits are handled gracefully
- Timeout errors are handled
- Error responses include helpful messages for debugging

## Technical Requirements

### TR-1: OpenRouter Integration
- Use httpx library for HTTP requests
- Use OpenRouter API endpoint: https://openrouter.ai/api/v1/chat/completions
- Use model: openai/gpt-oss-120b
- Set appropriate timeout (30 seconds)
- Include proper headers (Authorization, HTTP-Referer, X-Title)

### TR-2: Code Organization
- Create backend/ai.py module
- Function: load_openrouter_key() -> str
- Function: call_openrouter(prompt: str, model: str) -> str
- Keep functions simple and focused

### TR-3: Testing
- Unit tests with mocked HTTP calls
- Test success case
- Test missing API key
- Test network failure
- Test API error response
- Achieve 80%+ code coverage

## Non-Functional Requirements

### NFR-1: Performance
- AI calls should timeout after 30 seconds
- Endpoint should respond within 35 seconds total

### NFR-2: Security
- API key must not be logged
- API key must not appear in error messages
- All endpoints require authentication

### NFR-3: Maintainability
- Code follows project coding standards
- Functions are simple and focused
- Error messages are clear and actionable

## Out of Scope
- Structured outputs (Part 9)
- Board manipulation via AI (Part 9)
- Conversation history (Part 9)
- Chat UI (Part 10)
- Streaming responses
- Multiple AI models
- AI response caching

## Success Metrics
- All unit tests pass with 80%+ coverage
- Manual test with curl succeeds
- Error cases handled gracefully
- Code review passes
