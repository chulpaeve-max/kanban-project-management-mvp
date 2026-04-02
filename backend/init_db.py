import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Board, BoardColumn
from database import DATABASE_URL


def init_database():
    """Initialize database with default user and board."""
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if default user exists
        existing_user = db.query(User).filter(User.username == "user").first()
        if existing_user:
            print("Default user already exists")
            return
        
        # Create default user
        user = User(username="user", hashed_password="password")
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created default user: {user.username}")
        
        # Create default board
        board = Board(user_id=user.id, title="My Board")
        db.add(board)
        db.commit()
        db.refresh(board)
        print(f"Created default board: {board.title}")
        
        # Create default columns
        column_titles = ["Backlog", "Discovery", "In Progress", "Review", "Done"]
        for idx, title in enumerate(column_titles):
            column = BoardColumn(board_id=board.id, title=title, position=idx)
            db.add(column)
        
        db.commit()
        print(f"Created {len(column_titles)} default columns")
        
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
