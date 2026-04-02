import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Base, User, Board, BoardColumn
from backend.init_db import init_database
from backend.database import DATABASE_URL


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database for testing."""
    db_path = tmp_path / "test_kanban.db"
    original_url = DATABASE_URL
    
    # Temporarily override DATABASE_URL
    import backend.init_db
    backend.init_db.DATABASE_URL = f"sqlite:///{db_path}"
    
    yield db_path
    
    # Cleanup
    backend.init_db.DATABASE_URL = original_url
    if db_path.exists():
        db_path.unlink()


def test_creates_default_user(temp_db, capsys):
    """Test that init_database creates default user."""
    init_database()
    
    # Verify output
    captured = capsys.readouterr()
    assert "Created default user: user" in captured.out
    
    # Verify in database
    engine = create_engine(f"sqlite:///{temp_db}")
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    user = db.query(User).filter(User.username == "user").first()
    assert user is not None
    assert user.username == "user"
    assert user.hashed_password == "password"
    
    db.close()


def test_creates_default_board(temp_db, capsys):
    """Test that init_database creates default board with columns."""
    init_database()
    
    # Verify output
    captured = capsys.readouterr()
    assert "Created default board: My Board" in captured.out
    assert "Created 5 default columns" in captured.out
    
    # Verify in database
    engine = create_engine(f"sqlite:///{temp_db}")
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    user = db.query(User).filter(User.username == "user").first()
    board = db.query(Board).filter(Board.user_id == user.id).first()
    
    assert board is not None
    assert board.title == "My Board"
    
    columns = db.query(BoardColumn).filter(BoardColumn.board_id == board.id).all()
    assert len(columns) == 5
    
    column_titles = [col.title for col in sorted(columns, key=lambda c: c.position)]
    assert column_titles == ["Backlog", "Discovery", "In Progress", "Review", "Done"]
    
    db.close()


def test_skips_if_user_exists(temp_db, capsys):
    """Test that init_database skips creation if user already exists."""
    # Run once
    init_database()
    
    # Run again
    init_database()
    
    captured = capsys.readouterr()
    assert "Default user already exists" in captured.out
    
    # Verify only one user exists
    engine = create_engine(f"sqlite:///{temp_db}")
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    user_count = db.query(User).filter(User.username == "user").count()
    assert user_count == 1
    
    db.close()
