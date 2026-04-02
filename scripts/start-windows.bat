@echo off

docker info >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running. Please start Docker and try again.
    exit /b 1
)

echo Starting Kanban Studio...
docker-compose up --build
