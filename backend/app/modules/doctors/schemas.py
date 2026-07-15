import uuid
from datetime import date, datetime

from pydantic import BaseModel, field_validator


class DoctorProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    full_name: str | None = None
    specialization: str | None = None
    license_number: str | None = None
    years_experience: int | None = None
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DoctorPublicProfileResponse(BaseModel):
    """Reduced view shown to patients browsing/selecting a doctor - no license number exposed."""
    id: uuid.UUID
    full_name: str | None = None
    specialization: str | None = None
    years_experience: int | None = None
    is_verified: bool

    class Config:
        from_attributes = True


class DoctorProfileUpdateRequest(BaseModel):
    full_name: str | None = None
    specialization: str | None = None
    years_experience: int | None = None

    @field_validator("years_experience")
    @classmethod
    def validate_experience(cls, v: int | None) -> int | None:
        if v is not None and not (0 <= v <= 70):
            raise ValueError("years_experience must be between 0 and 70")
        return v


class PatientSummary(BaseModel):
    """Summary view of an assigned patient, shown in a doctor's patient list."""
    id: uuid.UUID
    full_name: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None

    class Config:
        from_attributes = True


class PatientNoteCreateRequest(BaseModel):
    patient_id: uuid.UUID
    note: str

    @field_validator("note")
    @classmethod
    def validate_note(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("note cannot be empty")
        if len(v) > 5000:
            raise ValueError("note must be under 5000 characters")
        return v


class PatientNoteResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    doctor_id: uuid.UUID
    note: str
    created_at: datetime

    class Config:
        from_attributes = True
