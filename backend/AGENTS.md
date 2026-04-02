# Backend - Kanban Studio API

## Overview

FastAPI backend serving the Kanban Studio application. Provides REST API endpoints and serves static frontend files.

## Tech Stack

- FastAPI 0.115.0
- Uvicorn 0.32.0 (ASGI server)
- SQLAlchemy 2.0.36 (ORM)
- Pydantic 2.9.2 (validation)
- httpx 0.27.2 (HTTP client for OpenRouter)
- python-dotenv 1.0.1 (environment variables)
- pytest 8.3.3 (testing)

## Architecture

### Entry Point
- `main.py` - FastAPI application with CORS middleware

### Current Endpoints
- `GET /` - Serves HTML "Hello World" page
- `GET /api/health` - Health check endpoint returning {"status": "ok"}

## Configuration

- Port: 8000
- CORS: Enabled for all origins (development)
- Database: SQLite at /app/data/kanban.db (configured via DATABASE_URL env var)

## Testing

- pytest with coverage reporting
- Test files in `tests/` directory
- Run: `pytest` from backend directory
- Coverage target: 80%+

## Docker

- Python 3.12 slim base image
- uv package manager for dependencies
- Exposed on port 8000
- Volume mount for SQLite persistence at /app/data