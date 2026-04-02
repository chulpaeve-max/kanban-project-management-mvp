import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app

client = TestClient(app)

def test_api_routes_separate():
    """Verify /api/* routes are handled separately from frontend"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_frontend_loads():
    """Test that root route loads (either frontend or fallback)"""
    response = client.get("/")
    assert response.status_code == 200
