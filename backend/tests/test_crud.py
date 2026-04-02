import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Base, User, Board, BoardColumn, Card
from backend import crud


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(username="testuser", hashed_password="testpass")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_board(db_session, test_user):
    """Create a test board with columns."""
    board = Board(user_id=test_user.id, title="Test Board")
    db_session.add(board)
    db_session.commit()
    db_session.refresh(board)
    
    # Add columns
    for i, title in enumerate(["Todo", "Doing", "Done"]):
        column = BoardColumn(board_id=board.id, title=title, position=i)
        db_session.add(column)
    db_session.commit()
    
    return board


def test_get_user_by_username(db_session, test_user):
    """Test getting user by username."""
    user = crud.get_user_by_username(db_session, "testuser")
    assert user is not None
    assert user.username == "testuser"
    
    # Test non-existent user
    user = crud.get_user_by_username(db_session, "nonexistent")
    assert user is None


def test_get_board_by_user_id(db_session, test_user, test_board):
    """Test getting board by user ID."""
    board = crud.get_board_by_user_id(db_session, test_user.id)
    assert board is not None
    assert board.id == test_board.id
    assert board.title == "Test Board"
    assert len(board.columns) == 3
    
    # Test non-existent user
    board = crud.get_board_by_user_id(db_session, 9999)
    assert board is None


def test_create_board(db_session, test_user):
    """Test creating a board."""
    board = crud.create_board(db_session, test_user.id, "New Board")
    assert board.id is not None
    assert board.title == "New Board"
    assert board.user_id == test_user.id


def test_update_column_title(db_session, test_board):
    """Test updating column title."""
    column = test_board.columns[0]
    updated = crud.update_column_title(db_session, column.id, "Updated Title")
    assert updated is not None
    assert updated.title == "Updated Title"
    
    # Test non-existent column
    updated = crud.update_column_title(db_session, 9999, "Title")
    assert updated is None


def test_create_card(db_session, test_board):
    """Test creating a card."""
    column = test_board.columns[0]
    card = crud.create_card(db_session, column.id, "Test Card", "Details here", 0)
    assert card.id is not None
    assert card.title == "Test Card"
    assert card.details == "Details here"
    assert card.column_id == column.id
    assert card.position == 0


def test_update_card(db_session, test_board):
    """Test updating a card."""
    column = test_board.columns[0]
    card = crud.create_card(db_session, column.id, "Original", "Original details", 0)
    
    # Update title only
    updated = crud.update_card(db_session, card.id, title="New Title")
    assert updated.title == "New Title"
    assert updated.details == "Original details"
    
    # Update details only
    updated = crud.update_card(db_session, card.id, details="New details")
    assert updated.title == "New Title"
    assert updated.details == "New details"
    
    # Test non-existent card
    updated = crud.update_card(db_session, 9999, title="Title")
    assert updated is None


def test_delete_card(db_session, test_board):
    """Test deleting a card."""
    column = test_board.columns[0]
    card = crud.create_card(db_session, column.id, "To Delete", "", 0)
    
    success = crud.delete_card(db_session, card.id)
    assert success is True
    
    # Verify card is deleted
    deleted_card = db_session.query(Card).filter(Card.id == card.id).first()
    assert deleted_card is None
    
    # Test non-existent card
    success = crud.delete_card(db_session, 9999)
    assert success is False


def test_move_card(db_session, test_board):
    """Test moving a card."""
    column1 = test_board.columns[0]
    column2 = test_board.columns[1]
    card = crud.create_card(db_session, column1.id, "Move Me", "", 0)
    
    moved = crud.move_card(db_session, card.id, column2.id, 1)
    assert moved is not None
    assert moved.column_id == column2.id
    assert moved.position == 1
    
    # Test non-existent card
    moved = crud.move_card(db_session, 9999, column2.id, 0)
    assert moved is None


def test_move_card_to_empty_column(db_session, test_user):
    """Test moving a card to an empty column."""
    # Create board with empty column
    board = Board(user_id=test_user.id, title="Test Board")
    db_session.add(board)
    db_session.commit()
    
    col1 = BoardColumn(board_id=board.id, title="Source", position=0)
    col2 = BoardColumn(board_id=board.id, title="Empty Target", position=1)
    db_session.add(col1)
    db_session.add(col2)
    db_session.commit()
    
    # Create card in first column
    card = crud.create_card(db_session, col1.id, "Test Card", "", 0)
    
    # Move to empty column at position 0
    moved = crud.move_card(db_session, card.id, col2.id, 0)
    assert moved is not None
    assert moved.column_id == col2.id
    assert moved.position == 0
