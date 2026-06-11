import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Board, BoardColumn
from database import DATABASE_URL


def init_database():
    """Initialize database with default user and board."""
    print("Starting database initialization...")
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if default user exists
        existing_user = db.query(User).filter(User.username == "user").first()
        if existing_user:
            print("Default user already exists")
            # Check if user has a board
            existing_board = db.query(Board).filter(Board.user_id == existing_user.id).first()
            if existing_board:
                print("User already has a board")
                return
            else:
                print("Creating board for existing user...")
                user = existing_user
        else:
            # Create default user
            print("Creating default user...")
            user = User(username="user", hashed_password="password")
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created default user: {user.username}")
        
        # Create default board
        print("Creating default board...")
        board = Board(user_id=user.id, title="My Board")
        db.add(board)
        db.commit()
        db.refresh(board)
        print(f"Created default board: {board.title}")
        
        # Create default columns
        print("Creating default columns...")
        column_titles = ["Backlog", "Discovery", "In Progress", "Review", "Done"]
        for idx, title in enumerate(column_titles):
            column = BoardColumn(board_id=board.id, title=title, position=idx)
            db.add(column)
        
        db.commit()
        print(f"Created {len(column_titles)} default columns")
        print("Database initialization complete!")
        
    except Exception as e:
        print(f"Error during database initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
