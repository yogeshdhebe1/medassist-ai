import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator


class SymptomCheckerRequest(BaseModel):
    symptoms: list[str]

    @field_validator("symptoms")
    @classmethod
    def validate_symptoms(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("At least one symptom is required")
        if len(v) > 30:
            raise ValueError("Please limit to 30 symptoms per check")
        return [s.strip().lower() for s in v]


class DiseasePredictionItem(BaseModel):
    disease: str
    confidence: float
    explanation: str


class SymptomCheckerResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    prediction_id: uuid.UUID
    predictions: list[DiseasePredictionItem]
    recommend_doctor_visit: bool
    recognized_symptoms: list[str]
    unrecognized_symptoms: list[str]
    model_version: str
    created_at: datetime


class KnownSymptomsResponse(BaseModel):
    symptoms: list[str]
    count: int
