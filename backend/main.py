from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
from typing import Optional
from auth import (
    verify_credentials,
    create_session_token,
    verify_session_token,
    clear_session
)
from database import get_db
from schemas import (
    BoardSchema,
    CardSchema,
    UpdateColumnRequest,
    CreateCardRequest,
    UpdateCardRequest,
    MoveCardRequest,
    TestAIRequest,
    TestAIResponse,
    AIRequest,
    AIResponse,
    BoardUpdate,
    CardUpdate
)
import crud
import ai
from prompts import get_system_prompt, format_conversation_history

app = FastAPI(title="Kanban Studio API")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup."""
    print("=" * 50)
    print("APPLICATION STARTUP")
    print("=" * 50)
    try:
        from init_db import init_database
        init_database()
        print("Database initialization completed successfully")
    except Exception as e:
        print(f"ERROR during database initialization: {e}")
        import traceback
        traceback.print_exc()
    print("=" * 50)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    username: str

class UserResponse(BaseModel):
    username: str

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    if not verify_credentials(db, request.username, request.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_session_token(request.username)
    return LoginResponse(token=token, username=request.username)

@app.post("/api/auth/logout")
async def logout(authorization: Optional[str] = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        clear_session(token)
    return {"message": "Logged out"}

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    username = verify_session_token(token)
    
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return UserResponse(username=username)

@app.get("/api/health")
async def health():
    return {"status": "ok"}

# Helper function to get current user from token
def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    username = verify_session_token(token)
    
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = crud.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

# Board API endpoints
@app.get("/api/board", response_model=BoardSchema)
async def get_board(user = Depends(get_current_user), db: Session = Depends(get_db)):
    board = crud.get_board_by_user_id(db, user.id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board

@app.put("/api/columns/{column_id}")
async def rename_column(column_id: int, request: UpdateColumnRequest, user = Depends(get_current_user), db: Session = Depends(get_db)):
    column = crud.update_column_title(db, column_id, request.title)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    return {"id": column.id, "title": column.title}

@app.post("/api/cards", response_model=CardSchema)
async def create_card(request: CreateCardRequest, user = Depends(get_current_user), db: Session = Depends(get_db)):
    from models import Card
    max_position = db.query(Card).filter(Card.column_id == request.column_id).count()
    card = crud.create_card(db, request.column_id, request.title, request.details, max_position)
    return card

@app.put("/api/cards/{card_id}", response_model=CardSchema)
async def update_card(card_id: int, request: UpdateCardRequest, user = Depends(get_current_user), db: Session = Depends(get_db)):
    card = crud.update_card(db, card_id, request.title, request.details)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card

@app.delete("/api/cards/{card_id}")
async def delete_card(card_id: int, user = Depends(get_current_user), db: Session = Depends(get_db)):
    success = crud.delete_card(db, card_id)
    if not success:
        raise HTTPException(status_code=404, detail="Card not found")
    return {"message": "Card deleted"}

@app.put("/api/cards/{card_id}/move", response_model=CardSchema)
async def move_card(card_id: int, request: MoveCardRequest, user = Depends(get_current_user), db: Session = Depends(get_db)):
    card = crud.move_card(db, card_id, request.target_column_id, request.position)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card

@app.post("/api/ai/test", response_model=TestAIResponse)
async def test_ai(request: TestAIRequest, user = Depends(get_current_user)):
    try:
        response = ai.call_openrouter(request.prompt)
        return TestAIResponse(response=response)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=503, detail="AI service unavailable")

@app.post("/api/ai/chat", response_model=AIResponse)
async def ai_chat(request: AIRequest, user = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # Get user's board
        board = crud.get_board_by_user_id(db, user.id)
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
        
        # Convert board to dict for prompt
        board_data = {
            "id": board.id,
            "title": board.title,
            "columns": [
                {
                    "id": col.id,
                    "title": col.title,
                    "position": col.position,
                    "cards": [
                        {
                            "id": card.id,
                            "title": card.title,
                            "details": card.details,
                            "position": card.position
                        }
                        for card in sorted(col.cards, key=lambda c: c.position)
                    ]
                }
                for col in sorted(board.columns, key=lambda c: c.position)
            ]
        }
        
        # Generate system prompt
        system_prompt = get_system_prompt(board_data)
        
        # Format conversation history
        history = format_conversation_history([
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ])
        
        # Call AI
        ai_response = ai.call_openrouter_structured(
            system_prompt=system_prompt,
            user_message=request.message,
            conversation_history=history
        )
        
        # Apply board updates if present
        if "board_update" in ai_response and ai_response["board_update"]:
            board_update = ai_response["board_update"]
            if "cards" in board_update:
                for card_update in board_update["cards"]:
                    action = card_update.get("action")
                    
                    if action == "create":
                        # Get max position for column
                        from models import Card
                        max_pos = db.query(Card).filter(
                            Card.column_id == card_update["column_id"]
                        ).count()
                        crud.create_card(
                            db,
                            column_id=card_update["column_id"],
                            title=card_update["title"],
                            details=card_update.get("details", ""),
                            position=card_update.get("position", max_pos)
                        )
                    
                    elif action == "move":
                        crud.move_card(
                            db,
                            card_id=card_update["id"],
                            target_column_id=card_update["column_id"],
                            position=card_update["position"]
                        )
                    
                    elif action == "update":
                        crud.update_card(
                            db,
                            card_id=card_update["id"],
                            title=card_update.get("title"),
                            details=card_update.get("details")
                        )
                    
                    elif action == "delete":
                        crud.delete_card(db, card_update["id"])
        
        return AIResponse(
            response=ai_response.get("response", ""),
            board_update=BoardUpdate(**ai_response.get("board_update", {})) if "board_update" in ai_response else None
        )
        
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=503, detail="AI service unavailable")

# Mount static files from frontend build
static_dir = "/app/frontend/out"
if os.path.exists(static_dir):
    app.mount("/_next", StaticFiles(directory=f"{static_dir}/_next"), name="next-static")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api/"):
            return {"error": "Not found"}
        
        file_path = os.path.join(static_dir, full_path if full_path else "index.html")
        
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        
        return {"error": "Not found"}
