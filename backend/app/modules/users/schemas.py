import uuid
from datetime import datetime

from pydantic import BaseModel


class UserSummaryResponse(BaseModel):
    id: uuid.UUID
    email: str
    phone: str | None
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserStatusUpdateRequest(BaseModel):
    is_active: bool
