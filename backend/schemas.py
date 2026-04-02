from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CardSchema(BaseModel):
    id: int
    title: str
    details: Optional[str] = None
    position: int
    
    class Config:
        from_attributes = True

class ColumnSchema(BaseModel):
    id: int
    title: str
    position: int
    cards: List[CardSchema] = []
    
    class Config:
        from_attributes = True

class BoardSchema(BaseModel):
    id: int
    title: str
    columns: List[ColumnSchema] = []
    
    class Config:
        from_attributes = True

class UserSchema(BaseModel):
    id: int
    username: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Request schemas
class UpdateColumnRequest(BaseModel):
    title: str

class CreateCardRequest(BaseModel):
    column_id: int
    title: str
    details: Optional[str] = ""

class UpdateCardRequest(BaseModel):
    title: Optional[str] = None
    details: Optional[str] = None

class MoveCardRequest(BaseModel):
    target_column_id: int
    position: int

class TestAIRequest(BaseModel):
    prompt: str

class TestAIResponse(BaseModel):
    response: str

# AI Chat schemas
class AIMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class CardUpdate(BaseModel):
    id: Optional[int] = None
    column_id: Optional[int] = None
    title: Optional[str] = None
    details: Optional[str] = None
    position: Optional[int] = None
    action: str  # "create", "update", "delete", "move"

class BoardUpdate(BaseModel):
    cards: List[CardUpdate] = []

class AIRequest(BaseModel):
    message: str
    conversation_history: List[AIMessage] = []

class AIResponse(BaseModel):
    response: str
    board_update: Optional[BoardUpdate] = None
