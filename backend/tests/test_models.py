import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import Base, User, Board, BoardColumn, Card

@pytest.fixture
def db_session():
    """Create a test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_create_user(db_session):
    user = User(username="testuser", password="testpass")
    db_session.add(user)
    db_session.commit()
    
    assert user.id is not None
    assert user.username == "testuser"
    assert user.created_at is not None

def test_create_board(db_session):
    user = User(username="testuser", password="testpass")
    db_session.add(user)
    db_session.commit()
    
    board = Board(user_id=user.id, title="Test Board")
    db_session.add(board)
    db_session.commit()
    
    assert board.id is not None
    assert board.user_id == user.id
    assert board.title == "Test Board"

def test_create_column(db_session):
    user = User(username="testuser", password="testpass")
    db_session.add(user)
    db_session.flush()  # Flush to get user.id
    
    board = Board(user_id=user.id, title="Test Board")
    db_session.add(board)
    db_session.flush()  # Flush to get board.id
    
    column = BoardColumn(board_id=board.id, title="Backlog", position=0)
    db_session.add(column)
    db_session.commit()
    
    assert column.id is not None
    assert column.board_id == board.id
    assert column.title == "Backlog"
    assert column.position == 0

def test_create_card(db_session):
    user = User(username="testuser", password="testpass")
    db_session.add(user)
    db_session.flush()
    
    board = Board(user_id=user.id, title="Test Board")
    db_session.add(board)
    db_session.flush()
    
    column = BoardColumn(board_id=board.id, title="Backlog", position=0)
    db_session.add(column)
    db_session.flush()
    
    card = Card(column_id=column.id, title="Test Card", details="Test details", position=0)
    db_session.add(card)
    db_session.commit()
    
    assert card.id is not None
    assert card.column_id == column.id
    assert card.title == "Test Card"
    assert card.details == "Test details"
    assert card.position == 0

def test_relationships(db_session):
    user = User(username="testuser", password="testpass")
    db_session.add(user)
    db_session.flush()
    
    board = Board(user_id=user.id, title="Test Board")
    db_session.add(board)
    db_session.flush()
    
    column = BoardColumn(board_id=board.id, title="Backlog", position=0)
    db_session.add(column)
    db_session.flush()
    
    card = Card(column_id=column.id, title="Test Card", details="Test details", position=0)
    db_session.add(card)
    db_session.commit()
    
    # Test relationships
    assert user.boards[0].id == board.id
    assert board.columns[0].id == column.id
    assert column.cards[0].id == card.id
    assert card.column.id == column.id
