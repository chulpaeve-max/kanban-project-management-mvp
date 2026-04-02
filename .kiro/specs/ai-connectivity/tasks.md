# AI Connectivity - Implementation Tasks

## Task 1: Create backend/ai.py module

Create the AI integration module with OpenRouter connectivity.

### Subtasks:
- [ ] 1.1 Create backend/ai.py file
- [ ] 1.2 Implement load_openrouter_key() function
  - Read OPENROUTER_API_KEY from environment
  - Raise ValueError if missing
  - Do not log the key value
- [ ] 1.3 Implement call_openrouter() function
  - Accept prompt and model parameters
  - Use httpx.Client for HTTP request
  - Set 30-second timeout
  - Set proper headers (Authorization, Content-Type, HTTP-Referer, X-Title)
  - Format request body with messages array
  - Parse response and extract content
  - Handle errors (timeout, HTTP errors)

## Task 2: Update backend/schemas.py

Add Pydantic schemas for AI test endpoint.

### Subtasks:
- [ ] 2.1 Add TestAIRequest schema
  - prompt: str field
- [ ] 2.2 Add TestAIResponse schema
  - response: str field

## Task 3: Update backend/main.py

Add the AI test endpoint to FastAPI application.

### Subtasks:
- [ ] 3.1 Import ai module and new schemas
- [ ] 3.2 Create POST /api/ai/test endpoint
  - Require authentication (use get_current_user dependency)
  - Accept TestAIRequest
  - Call ai.call_openrouter()
  - Return TestAIResponse
  - Handle exceptions and return appropriate HTTP errors

## Task 4: Create backend/tests/test_ai.py

Write unit tests for AI module.

### Subtasks:
- [ ] 4.1 Create test file with fixtures
- [ ] 4.2 Implement test_load_openrouter_key_success
  - Mock os.getenv to return test key
  - Verify function returns key
- [ ] 4.3 Implement test_load_openrouter_key_missing
  - Mock os.getenv to return None
  - Verify ValueError is raised
- [ ] 4.4 Implement test_call_openrouter_success
  - Mock httpx.post to return success response
  - Verify request format (URL, headers, body)
  - Verify response parsing
- [ ] 4.5 Implement test_call_openrouter_timeout
  - Mock httpx.post to raise TimeoutException
  - Verify exception is raised
- [ ] 4.6 Implement test_call_openrouter_http_error
  - Mock httpx.post to raise HTTPError
  - Verify exception is raised
- [ ] 4.7 Verify 80%+ code coverage for ai.py

## Task 5: Update backend/tests/test_main.py

Add integration tests for AI test endpoint.

### Subtasks:
- [ ] 5.1 Implement test_ai_test_endpoint_success
  - Mock ai.call_openrouter
  - Create authenticated request
  - Verify response format
- [ ] 5.2 Implement test_ai_test_endpoint_unauthenticated
  - Send request without auth token
  - Verify 401 response
- [ ] 5.3 Implement test_ai_test_endpoint_ai_failure
  - Mock ai.call_openrouter to raise exception
  - Verify error response (500 or 503)
- [ ] 5.4 Verify overall test coverage remains 80%+

## Task 6: Verify .env configuration

Ensure OpenRouter API key is configured.

### Subtasks:
- [ ] 6.1 Check .env file has OPENROUTER_API_KEY
- [ ] 6.2 Verify key is valid (non-empty string)
- [ ] 6.3 Document in README if needed

## Task 7: Manual testing

Test the implementation end-to-end.

### Subtasks:
- [ ] 7.1 Rebuild Docker container
- [ ] 7.2 Start application
- [ ] 7.3 Login and get auth token
- [ ] 7.4 Call POST /api/ai/test with prompt "2+2"
- [ ] 7.5 Verify response is reasonable
- [ ] 7.6 Test error cases (invalid token, missing API key)

## Task 8: Update documentation

Update project documentation.

### Subtasks:
- [ ] 8.1 Mark Part 8 tasks as complete in docs/PLAN.md
- [ ] 8.2 Update docs/SESSION_SUMMARY.md if needed
