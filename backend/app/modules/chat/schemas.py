import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator


class ChatSessionResponse(BaseModel):
    session_id: uuid.UUID


class ChatMessageRequest(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("message cannot be empty")
        if len(v) > 1000:
            raise ValueError("message must be under 1000 characters")
        return v


class ChatMessageResponse(BaseModel):
    reply: str
    disclaimer: str


class ChatMessageHistoryItem(BaseModel):
    id: uuid.UUID
    sender: str
    message: str
    sent_at: datetime

    class Config:
        from_attributes = True
