import uuid
from datetime import date, datetime

from pydantic import BaseModel, field_validator


class PatientProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    full_name: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    blood_group: str | None = None
    medical_history: dict = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PatientProfileUpdateRequest(BaseModel):
    full_name: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    blood_group: str | None = None
    medical_history: dict | None = None

    @field_validator("height_cm")
    @classmethod
    def validate_height(cls, v: float | None) -> float | None:
        if v is not None and not (30 <= v <= 300):
            raise ValueError("height_cm must be between 30 and 300")
        return v

    @field_validator("weight_kg")
    @classmethod
    def validate_weight(cls, v: float | None) -> float | None:
        if v is not None and not (1 <= v <= 500):
            raise ValueError("weight_kg must be between 1 and 500")
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: date | None) -> date | None:
        if v is not None and v >= date.today():
            raise ValueError("date_of_birth must be in the past")
        return v
