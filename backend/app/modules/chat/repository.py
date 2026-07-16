import uuid

from sqlalchemy.orm import Session

from app.modules.chat.models import ChatSession, ChatMessage


class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_session(self, session_id: uuid.UUID) -> ChatSession | None:
        return self.db.query(ChatSession).filter(ChatSession.id == session_id).first()

    def create_session(self, patient_id: uuid.UUID) -> ChatSession:
        session = ChatSession(patient_id=patient_id)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def add_message(self, session_id: uuid.UUID, sender: str, message: str) -> ChatMessage:
        record = ChatMessage(session_id=session_id, sender=sender, message=message)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_messages(self, session_id: uuid.UUID, page: int = 1, page_size: int = 50) -> list[ChatMessage]:
        return (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.sent_at.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
