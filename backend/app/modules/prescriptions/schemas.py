import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator


class MedicationItem(BaseModel):
    name: str
    dosage: str
    frequency: str
    duration_days: int

    @field_validator("name", "dosage", "frequency")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("field cannot be empty")
        return v

    @field_validator("duration_days")
    @classmethod
    def validate_duration(cls, v: int) -> int:
        if not (1 <= v <= 365):
            raise ValueError("duration_days must be between 1 and 365")
        return v


class PrescriptionCreateRequest(BaseModel):
    patient_id: uuid.UUID
    medications: list[MedicationItem]
    notes: str | None = None

    @field_validator("medications")
    @classmethod
    def at_least_one_medication(cls, v: list[MedicationItem]) -> list[MedicationItem]:
        if not v:
            raise ValueError("At least one medication is required")
        return v

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 2000:
            raise ValueError("notes must be under 2000 characters")
        return v


class PrescriptionResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    doctor_id: uuid.UUID
    medications: list[MedicationItem]
    notes: str | None
    issued_at: datetime

    class Config:
        from_attributes = True
