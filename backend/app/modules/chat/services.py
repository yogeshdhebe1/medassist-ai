import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.modules.chat.bot_engine import generate_reply, DISCLAIMER
from app.modules.chat.models import ChatSession, ChatMessage
from app.modules.chat.repository import ChatRepository
from app.modules.patients.repository import PatientRepository


class ChatService:
    def __init__(self, db: Session):
        self.repo = ChatRepository(db)
        self.patient_repo = PatientRepository(db)

    def start_session(self, patient_user_id: uuid.UUID) -> ChatSession:
        patient = self.patient_repo.get_by_user_id(patient_user_id)
        if not patient:
            patient = self.patient_repo.create(patient_user_id)
        return self.repo.create_session(patient.id)

    def _authorize_session(self, session_id: uuid.UUID, patient_user_id: uuid.UUID) -> ChatSession:
        session = self.repo.get_session(session_id)
        if not session:
            raise NotFoundError("Chat session not found")

        patient = self.patient_repo.get_by_user_id(patient_user_id)
        if not patient or session.patient_id != patient.id:
            raise ForbiddenError("You do not have access to this chat session")

        return session

    def send_message(self, session_id: uuid.UUID, patient_user_id: uuid.UUID, message: str) -> dict:
        self._authorize_session(session_id, patient_user_id)

        self.repo.add_message(session_id, sender="user", message=message)
        reply_text = generate_reply(message)
        self.repo.add_message(session_id, sender="bot", message=reply_text)

        return {"reply": reply_text, "disclaimer": DISCLAIMER}

    def get_history(self, session_id: uuid.UUID, patient_user_id: uuid.UUID, page: int, page_size: int) -> list[ChatMessage]:
        self._authorize_session(session_id, patient_user_id)
        return self.repo.list_messages(session_id, page, page_size)
