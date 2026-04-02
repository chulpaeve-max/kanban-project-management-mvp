import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app
from database import get_db
from models import Base, User
from auth import sessions

# Test database setup
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(bind=engine)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_user():
    """Create test user before each test"""
    sessions.clear()
    db = TestingSessionLocal()
    # Clear existing users
    db.query(User).delete()
    # Create test user
    user = User(username="user", hashed_password="password")
    db.add(user)
    db.commit()
    db.close()
    yield
    # Cleanup
    sessions.clear()

def test_login_success():
    response = client.post("/api/auth/login", json={
        "username": "user",
        "password": "password"
    })
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["username"] == "user"
    assert len(data["token"]) > 0

def test_login_failure():
    response = client.post("/api/auth/login", json={
        "username": "user",
        "password": "wrong"
    })
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

def test_logout():
    # Login first
    login_response = client.post("/api/auth/login", json={
        "username": "user",
        "password": "password"
    })
    token = login_response.json()["token"]
    
    # Logout
    response = client.post("/api/auth/logout", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    
    # Verify token is cleared
    me_response = client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert me_response.status_code == 401

def test_me_authenticated():
    # Login first
    login_response = client.post("/api/auth/login", json={
        "username": "user",
        "password": "password"
    })
    token = login_response.json()["token"]
    
    # Get current user
    response = client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert response.json()["username"] == "user"

def test_me_unauthenticated():
    response = client.get("/api/auth/me")
    assert response.status_code == 401

def test_me_invalid_token():
    response = client.get("/api/auth/me", headers={
        "Authorization": "Bearer invalid_token"
    })
    assert response.status_code == 401
