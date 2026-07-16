import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.modules.authentication.models import User
from app.modules.chat.schemas import (
    ChatSessionResponse,
    ChatMessageRequest,
    ChatMessageResponse,
    ChatMessageHistoryItem,
)
from app.modules.chat.services import ChatService

router = APIRouter(prefix="/chat", tags=["AI Health Chatbot"])


@router.post("/sessions", response_model=ChatSessionResponse, status_code=201)
def start_chat_session(
    current_user: User = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    session = ChatService(db).start_session(current_user.id)
    return {"session_id": session.id}


@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
def send_message(
    session_id: uuid.UUID,
    payload: ChatMessageRequest,
    current_user: User = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    return ChatService(db).send_message(session_id, current_user.id, payload.message)


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageHistoryItem])
def get_message_history(
    session_id: uuid.UUID,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    return ChatService(db).get_history(session_id, current_user.id, page, page_size)
