# Kanban Project Management MVP

AI-powered Kanban board for project management with intelligent task automation.

## Features

- User authentication (hardcoded for MVP: username `user`, password `password`)
- Drag-and-drop Kanban board with customizable columns
- AI chat assistant that can create, edit, and move cards
- Real-time board updates
- SQLite database for data persistence
- Dockerized deployment

## Tech Stack

- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Backend: Python FastAPI, SQLAlchemy
- Database: SQLite
- AI: OpenRouter API (`openai/gpt-oss-120b`)
- Deployment: Docker

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- OpenRouter API key

### Setup

1. Clone the repository
2. Create `.env` file in project root:
```
OPENROUTER_API_KEY=your_key_here
```

3. Run the appropriate start script:

**Mac/Linux:**
```bash
./scripts/start-mac.sh
# or
./scripts/start-linux.sh
```

**Windows:**
```bash
scripts\start-windows.bat
```

4. Open http://localhost:8000
5. Login with username `user` and password `password`

### Stopping

**Mac/Linux:**
```bash
./scripts/stop-mac.sh
# or
./scripts/stop-linux.sh
```

**Windows:**
```bash
scripts\stop-windows.bat
```

## Development

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm run test:unit
npm run test:e2e
```

## Project Structure

```
├── backend/          # FastAPI backend
├── frontend/         # Next.js frontend
├── data/            # SQLite database
├── docs/            # Documentation
├── scripts/         # Start/stop scripts
├── Dockerfile       # Container configuration
└── docker-compose.yml
```

## Color Scheme

- Accent Yellow: #ecad0a
- Blue Primary: #209dd7
- Purple Secondary: #753991
- Dark Navy: #032147
- Gray Text: #888888

## Documentation

See `docs/` directory for detailed documentation:
- `PLAN.md` - Implementation plan and progress
- `DATABASE.md` - Database schema
- `TESTING.md` - Testing strategy
