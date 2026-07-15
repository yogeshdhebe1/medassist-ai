import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator


class AppointmentCreateRequest(BaseModel):
    doctor_id: uuid.UUID
    scheduled_at: datetime
    reason: str | None = None

    @field_validator("scheduled_at")
    @classmethod
    def validate_future(cls, v: datetime) -> datetime:
        # Compare using naive-safe check: if the incoming datetime is timezone-aware,
        # compare against an aware "now"; the API layer/DB always stores timezone-aware values.
        now = datetime.now(v.tzinfo) if v.tzinfo else datetime.now()
        if v <= now:
            raise ValueError("scheduled_at must be in the future")
        return v

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 500:
            raise ValueError("reason must be under 500 characters")
        return v


class AppointmentStatusUpdateRequest(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = {"pending", "confirmed", "completed", "cancelled"}
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v


class AppointmentResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    doctor_id: uuid.UUID
    scheduled_at: datetime
    status: str
    reason: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
