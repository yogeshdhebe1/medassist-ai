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


class HeartDiseasePredictionRequest(BaseModel):
    age: int
    sex: int  # 1 = male, 0 = female
    cp: int  # chest pain type: 0-3
    trestbps: float  # resting blood pressure
    chol: float  # serum cholesterol
    fbs: int  # fasting blood sugar > 120 mg/dl: 1 = true, 0 = false
    restecg: int  # resting ECG results: 0-2
    thalach: float  # max heart rate achieved
    exang: int  # exercise-induced angina: 1 = yes, 0 = no
    oldpeak: float  # ST depression induced by exercise
    slope: int  # slope of peak exercise ST segment: 0-2
    ca: int  # number of major vessels colored by fluoroscopy: 0-3
    thal: int  # thalassemia: 1 = normal, 2 = fixed defect, 3 = reversible defect

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: int) -> int:
        if not (1 <= v <= 120):
            raise ValueError("age must be between 1 and 120")
        return v

    @field_validator("sex", "fbs", "exang")
    @classmethod
    def validate_binary(cls, v: int) -> int:
        if v not in (0, 1):
            raise ValueError("must be 0 or 1")
        return v

    @field_validator("cp", "restecg", "slope")
    @classmethod
    def validate_0_to_3(cls, v: int) -> int:
        if not (0 <= v <= 3):
            raise ValueError("must be between 0 and 3")
        return v

    @field_validator("trestbps")
    @classmethod
    def validate_trestbps(cls, v: float) -> float:
        if not (60 <= v <= 250):
            raise ValueError("trestbps must be between 60 and 250 mmHg")
        return v

    @field_validator("chol")
    @classmethod
    def validate_chol(cls, v: float) -> float:
        if not (100 <= v <= 600):
            raise ValueError("chol must be between 100 and 600 mg/dl")
        return v

    @field_validator("thalach")
    @classmethod
    def validate_thalach(cls, v: float) -> float:
        if not (60 <= v <= 250):
            raise ValueError("thalach must be between 60 and 250")
        return v

    @field_validator("oldpeak")
    @classmethod
    def validate_oldpeak(cls, v: float) -> float:
        if not (0 <= v <= 10):
            raise ValueError("oldpeak must be between 0 and 10")
        return v

    @field_validator("ca")
    @classmethod
    def validate_ca(cls, v: int) -> int:
        if not (0 <= v <= 4):
            raise ValueError("ca must be between 0 and 4")
        return v

    @field_validator("thal")
    @classmethod
    def validate_thal(cls, v: int) -> int:
        if v not in (0, 1, 2, 3):
            raise ValueError("thal must be 0, 1, 2, or 3")
        return v


class HeartDiseasePredictionResponse(BaseModel):
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
