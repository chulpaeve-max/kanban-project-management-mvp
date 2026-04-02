import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app, get_current_user
from database import get_db
from models import Base, User, Board, BoardColumn, Card
from auth import create_session_token

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

@pytest.fixture
def test_user():
    """Create a test user."""
    db = TestingSessionLocal()
    user = User(username="testuser", hashed_password="testpass")
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

@pytest.fixture
def test_board(test_user):
    """Create a test board with columns."""
    db = TestingSessionLocal()
    board = Board(user_id=test_user.id, title="Test Board")
    db.add(board)
    db.commit()
    db.refresh(board)
    
    for i, title in enumerate(["Todo", "Doing", "Done"]):
        column = BoardColumn(board_id=board.id, title=title, position=i)
        db.add(column)
    db.commit()
    
    db.refresh(board)
    db.close()
    return board

@pytest.fixture
def auth_headers(test_user):
    """Create auth headers with valid token."""
    token = create_session_token(test_user.username)
    return {"Authorization": f"Bearer {token}"}

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200

def test_get_board_authenticated(test_board, auth_headers):
    """Test getting board with authentication."""
    response = client.get("/api/board", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Board"
    assert len(data["columns"]) == 3
    assert data["columns"][0]["title"] == "Todo"

def test_get_board_unauthenticated():
    """Test getting board without authentication."""
    response = client.get("/api/board")
    assert response.status_code == 401

def test_rename_column(test_board, auth_headers):
    """Test renaming a column."""
    db = TestingSessionLocal()
    column = db.query(BoardColumn).first()
    column_id = column.id
    db.close()
    
    response = client.put(
        f"/api/columns/{column_id}",
        json={"title": "New Title"},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"

def test_create_card(test_board, auth_headers):
    """Test creating a card."""
    db = TestingSessionLocal()
    column = db.query(BoardColumn).first()
    column_id = column.id
    db.close()
    
    response = client.post(
        "/api/cards",
        json={"column_id": column_id, "title": "New Card", "details": "Details"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Card"
    assert data["details"] == "Details"
    assert data["column_id"] == column_id

def test_update_card(test_board, auth_headers):
    """Test updating a card."""
    db = TestingSessionLocal()
    column = db.query(BoardColumn).first()
    card = Card(column_id=column.id, title="Original", details="Original details", position=0)
    db.add(card)
    db.commit()
    db.refresh(card)
    card_id = card.id
    db.close()
    
    response = client.put(
        f"/api/cards/{card_id}",
        json={"title": "Updated", "details": "Updated details"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated"
    assert data["details"] == "Updated details"

def test_delete_card(test_board, auth_headers):
    """Test deleting a card."""
    db = TestingSessionLocal()
    column = db.query(BoardColumn).first()
    card = Card(column_id=column.id, title="To Delete", details="", position=0)
    db.add(card)
    db.commit()
    db.refresh(card)
    card_id = card.id
    db.close()
    
    response = client.delete(f"/api/cards/{card_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Card deleted"

def test_move_card(test_board, auth_headers):
    """Test moving a card."""
    db = TestingSessionLocal()
    columns = db.query(BoardColumn).all()
    column1 = columns[0]
    column2 = columns[1]
    card = Card(column_id=column1.id, title="Move Me", details="", position=0)
    db.add(card)
    db.commit()
    db.refresh(card)
    card_id = card.id
    db.close()
    
    response = client.put(
        f"/api/cards/{card_id}/move",
        json={"target_column_id": column2.id, "position": 1},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["column_id"] == column2.id
    assert data["position"] == 1


def test_move_card_to_empty_column(test_board, auth_headers):
    """Test moving a card to an empty column."""
    db = TestingSessionLocal()
    columns = db.query(BoardColumn).all()
    column1 = columns[0]
    column2 = columns[2]  # Use third column which should be empty
    
    # Create card in first column
    card = Card(column_id=column1.id, title="Move to Empty", details="", position=0)
    db.add(card)
    db.commit()
    db.refresh(card)
    card_id = card.id
    db.close()
    
    # Move to empty column at position 0
    response = client.put(
        f"/api/cards/{card_id}/move",
        json={"target_column_id": column2.id, "position": 0},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["column_id"] == column2.id
    assert data["position"] == 0


def test_ai_test_endpoint_success(test_user, auth_headers):
    """Test AI test endpoint with authentication."""
    from unittest.mock import patch
    
    with patch('ai.call_openrouter') as mock_call:
        mock_call.return_value = "The answer is 4"
        
        response = client.post(
            "/api/ai/test",
            json={"prompt": "2+2"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "The answer is 4"
        mock_call.assert_called_once_with("2+2")


def test_ai_test_endpoint_unauthenticated():
    """Test AI test endpoint without authentication."""
    response = client.post(
        "/api/ai/test",
        json={"prompt": "test"}
    )
    assert response.status_code == 401


def test_ai_test_endpoint_ai_failure(test_user, auth_headers):
    """Test AI test endpoint when AI service fails."""
    from unittest.mock import patch
    
    with patch('ai.call_openrouter') as mock_call:
        mock_call.side_effect = Exception("AI service error")
        
        response = client.post(
            "/api/ai/test",
            json={"prompt": "test"},
            headers=auth_headers
        )
        
        assert response.status_code == 503
        assert "unavailable" in response.json()["detail"]


def test_ai_test_endpoint_missing_api_key(test_user, auth_headers):
    """Test AI test endpoint when API key is missing."""
    from unittest.mock import patch
    
    with patch('ai.call_openrouter') as mock_call:
        mock_call.side_effect = ValueError("OPENROUTER_API_KEY not found")
        
        response = client.post(
            "/api/ai/test",
            json={"prompt": "test"},
            headers=auth_headers
        )
        
        assert response.status_code == 500



def test_ai_chat_text_only_response(test_board, auth_headers):
    """Test AI chat with text-only response."""
    from unittest.mock import patch
    
    with patch('ai.call_openrouter_structured') as mock_call:
        mock_call.return_value = {
            "response": "Your board has 3 columns"
        }
        
        response = client.post(
            "/api/ai/chat",
            json={
                "message": "What's on my board?",
                "conversation_history": []
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Your board has 3 columns"
        assert data["board_update"] is None


def test_ai_chat_with_board_update(test_board, auth_headers):
    """Test AI chat with board update."""
    from unittest.mock import patch
    
    db = TestingSessionLocal()
    column = db.query(BoardColumn).first()
    column_id = column.id
    db.close()
    
    with patch('ai.call_openrouter_structured') as mock_call:
        mock_call.return_value = {
            "response": "Created card Test",
            "board_update": {
                "cards": [
                    {
                        "action": "create",
                        "column_id": column_id,
                        "title": "Test Card",
                        "details": "Test details",
                        "position": 0
                    }
                ]
            }
        }
        
        response = client.post(
            "/api/ai/chat",
            json={
                "message": "Add a card called Test",
                "conversation_history": []
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Created card Test"
        assert data["board_update"] is not None
        
        # Verify card was created
        db = TestingSessionLocal()
        cards = db.query(Card).filter(Card.title == "Test Card").all()
        assert len(cards) == 1
        db.close()


def test_ai_chat_applies_board_changes(test_board, auth_headers):
    """Test that AI chat applies board changes to database."""
    from unittest.mock import patch
    
    db = TestingSessionLocal()
    columns = db.query(BoardColumn).all()
    col1 = columns[0]
    col2 = columns[1]
    
    # Create a card
    card = Card(column_id=col1.id, title="Move Me", details="", position=0)
    db.add(card)
    db.commit()
    db.refresh(card)
    card_id = card.id
    db.close()
    
    with patch('ai.call_openrouter_structured') as mock_call:
        mock_call.return_value = {
            "response": "Moved card",
            "board_update": {
                "cards": [
                    {
                        "action": "move",
                        "id": card_id,
                        "column_id": col2.id,
                        "position": 0
                    }
                ]
            }
        }
        
        response = client.post(
            "/api/ai/chat",
            json={
                "message": "Move card to Done",
                "conversation_history": []
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Verify card was moved
        db = TestingSessionLocal()
        card = db.query(Card).filter(Card.id == card_id).first()
        assert card.column_id == col2.id
        db.close()


def test_ai_chat_unauthenticated():
    """Test AI chat without authentication."""
    response = client.post(
        "/api/ai/chat",
        json={"message": "test", "conversation_history": []}
    )
    assert response.status_code == 401


def test_ai_chat_with_conversation_history(test_board, auth_headers):
    """Test AI chat with conversation history."""
    from unittest.mock import patch
    
    history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there"}
    ]
    
    with patch('ai.call_openrouter_structured') as mock_call:
        mock_call.return_value = {"response": "How can I help?"}
        
        response = client.post(
            "/api/ai/chat",
            json={
                "message": "What can you do?",
                "conversation_history": history
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Verify history was passed to AI
        call_args = mock_call.call_args
        assert call_args[1]["conversation_history"] is not None
