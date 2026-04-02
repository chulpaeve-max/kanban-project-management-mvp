#!/bin/bash

if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "Starting Kanban Studio..."
docker-compose up --build
