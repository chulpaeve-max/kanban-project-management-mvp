import secrets
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

# In-memory session store
sessions: dict[str, dict] = {}

def create_session_token(username: str) -> str:
    """Create a new session token for a user"""
    token = secrets.token_urlsafe(32)
    sessions[token] = {
        "username": username,
        "created_at": datetime.now()
    }
    return token

def verify_session_token(token: str) -> Optional[str]:
    """Verify a session token and return username if valid"""
    session = sessions.get(token)
    if not session:
        return None
    return session["username"]

def clear_session(token: str) -> None:
    """Clear a session token"""
    if token in sessions:
        del sessions[token]

def verify_credentials(db: Session, username: str, password: str) -> bool:
    """Verify username and password against database"""
    from models import User
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    # Simple password check (no hashing for MVP)
    return user.hashed_password == password
