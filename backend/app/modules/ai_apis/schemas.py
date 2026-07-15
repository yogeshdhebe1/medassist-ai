import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator


class DiabetesPredictionRequest(BaseModel):
    pregnancies: int
    glucose: float
    blood_pressure: float
    skin_thickness: float
    insulin: float
    bmi: float
    diabetes_pedigree: float
    age: int

    @field_validator("pregnancies")
    @classmethod
    def validate_pregnancies(cls, v: int) -> int:
        if not (0 <= v <= 20):
            raise ValueError("pregnancies must be between 0 and 20")
        return v

    @field_validator("glucose")
    @classmethod
    def validate_glucose(cls, v: float) -> float:
        if not (0 <= v <= 300):
            raise ValueError("glucose must be between 0 and 300 mg/dL")
        return v

    @field_validator("blood_pressure")
    @classmethod
    def validate_bp(cls, v: float) -> float:
        if not (0 <= v <= 200):
            raise ValueError("blood_pressure must be between 0 and 200 mmHg")
        return v

    @field_validator("bmi")
    @classmethod
    def validate_bmi(cls, v: float) -> float:
        if not (0 <= v <= 80):
            raise ValueError("bmi must be between 0 and 80")
        return v

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: int) -> int:
        if not (1 <= v <= 120):
            raise ValueError("age must be between 1 and 120")
        return v


class DiabetesPredictionResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    prediction_id: uuid.UUID
    risk_level: str
    probability: float
    contributing_factors: list[str]
    model_version: str
    created_at: datetime


class PredictionHistoryItem(BaseModel):
    model_config = {"protected_namespaces": (), "from_attributes": True}

    id: uuid.UUID
    prediction_type: str
    input_data: dict
    output_result: dict
    confidence_score: float | None
    model_version: str
    created_at: datetime
