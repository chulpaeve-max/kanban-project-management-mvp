# Use Python 3.12 slim image
FROM python:3.12-slim

# Install Node.js 20.x
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy and build frontend
COPY frontend/package*.json /app/frontend/
RUN cd /app/frontend && npm install

COPY frontend/ /app/frontend/
RUN cd /app/frontend && npm run build

# Copy backend requirements
COPY backend/requirements.txt /app/backend/requirements.txt

# Install Python dependencies using uv
RUN cd /app/backend && uv pip install --system -r requirements.txt

# Copy backend code
COPY backend/ /app/backend/

# Expose port 8000
EXPOSE 8000

# Set PYTHONPATH to include backend directory
ENV PYTHONPATH=/app/backend

# Create startup script that always initializes database
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Creating data directory..."\n\
mkdir -p /app/data\n\
echo "Initializing database..."\n\
cd /app/backend && python init_db.py\n\
echo "Starting server..."\n\
cd /app/backend && uvicorn main:app --host 0.0.0.0 --port 8000\n\
' > /app/start.sh && chmod +x /app/start.sh

# Run startup script
CMD ["/bin/bash", "/app/start.sh"]
