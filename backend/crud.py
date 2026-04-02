from sqlalchemy.orm import Session
from typing import Optional
import models
import schemas


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Get user by username."""
    return db.query(models.User).filter(models.User.username == username).first()


def get_board_by_user_id(db: Session, user_id: int) -> Optional[models.Board]:
    """Get board for a user with all columns and cards."""
    return db.query(models.Board).filter(models.Board.user_id == user_id).first()


def create_board(db: Session, user_id: int, title: str = "My Board") -> models.Board:
    """Create a new board for a user."""
    board = models.Board(user_id=user_id, title=title)
    db.add(board)
    db.commit()
    db.refresh(board)
    return board


def update_column_title(db: Session, column_id: int, title: str) -> Optional[models.BoardColumn]:
    """Update column title."""
    column = db.query(models.BoardColumn).filter(models.BoardColumn.id == column_id).first()
    if column:
        column.title = title
        db.commit()
        db.refresh(column)
    return column


def create_card(db: Session, column_id: int, title: str, details: str = "", position: int = 0) -> models.Card:
    """Create a new card in a column."""
    card = models.Card(
        column_id=column_id,
        title=title,
        details=details,
        position=position
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


def update_card(db: Session, card_id: int, title: Optional[str] = None, details: Optional[str] = None) -> Optional[models.Card]:
    """Update card title and/or details."""
    card = db.query(models.Card).filter(models.Card.id == card_id).first()
    if card:
        if title is not None:
            card.title = title
        if details is not None:
            card.details = details
        db.commit()
        db.refresh(card)
    return card


def delete_card(db: Session, card_id: int) -> bool:
    """Delete a card."""
    card = db.query(models.Card).filter(models.Card.id == card_id).first()
    if card:
        db.delete(card)
        db.commit()
        return True
    return False


def move_card(db: Session, card_id: int, target_column_id: int, position: int) -> Optional[models.Card]:
    """Move card to a different column and/or position."""
    print(f"🔧 [CRUD] move_card called: card_id={card_id}, target_column_id={target_column_id}, position={position}")
    
    card = db.query(models.Card).filter(models.Card.id == card_id).first()
    if not card:
        print(f"❌ [CRUD] Card not found: {card_id}")
        return None
    
    print(f"📋 [CRUD] Card found: id={card.id}, title='{card.title}', current_column={card.column_id}")
    
    # Verify target column exists
    target_column = db.query(models.BoardColumn).filter(models.BoardColumn.id == target_column_id).first()
    if not target_column:
        print(f"❌ [CRUD] Target column not found: {target_column_id}")
        return None
    
    print(f"📂 [CRUD] Target column found: id={target_column.id}, title='{target_column.title}'")
    
    # Update card's column and position
    old_column_id = card.column_id
    card.column_id = target_column_id
    card.position = position
    
    print(f"✅ [CRUD] Updating card: {old_column_id} -> {target_column_id}, position={position}")
    
    db.commit()
    db.refresh(card)
    
    print(f"✅ [CRUD] Card updated successfully")
    return card
