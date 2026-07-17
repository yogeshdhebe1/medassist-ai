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
    sex: int
    cp: int
    trestbps: float
    chol: float
    fbs: int
    restecg: int
    thalach: float
    exang: int
    oldpeak: float
    slope: int
    ca: int
    thal: int

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


class StrokePredictionRequest(BaseModel):
    gender: str  # 'Male', 'Female', 'Other'
    age: float
    hypertension: int  # 0 or 1
    heart_disease: int  # 0 or 1
    ever_married: str  # 'Yes' or 'No'
    work_type: str  # 'Private', 'Self-employed', 'Govt_job', 'children', 'Never_worked'
    residence_type: str  # 'Urban' or 'Rural'
    avg_glucose_level: float
    bmi: float
    smoking_status: str  # 'never smoked', 'formerly smoked', 'smokes', 'Unknown'

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        if v not in ("Male", "Female", "Other"):
            raise ValueError("gender must be 'Male', 'Female', or 'Other'")
        return v

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: float) -> float:
        if not (0 <= v <= 120):
            raise ValueError("age must be between 0 and 120")
        return v

    @field_validator("hypertension", "heart_disease")
    @classmethod
    def validate_binary(cls, v: int) -> int:
        if v not in (0, 1):
            raise ValueError("must be 0 or 1")
        return v

    @field_validator("ever_married")
    @classmethod
    def validate_ever_married(cls, v: str) -> str:
        if v not in ("Yes", "No"):
            raise ValueError("ever_married must be 'Yes' or 'No'")
        return v

    @field_validator("work_type")
    @classmethod
    def validate_work_type(cls, v: str) -> str:
        if v not in ("Private", "Self-employed", "Govt_job", "children", "Never_worked"):
            raise ValueError("invalid work_type")
        return v

    @field_validator("residence_type")
    @classmethod
    def validate_residence_type(cls, v: str) -> str:
        if v not in ("Urban", "Rural"):
            raise ValueError("residence_type must be 'Urban' or 'Rural'")
        return v

    @field_validator("avg_glucose_level")
    @classmethod
    def validate_glucose(cls, v: float) -> float:
        if not (40 <= v <= 400):
            raise ValueError("avg_glucose_level must be between 40 and 400")
        return v

    @field_validator("bmi")
    @classmethod
    def validate_bmi(cls, v: float) -> float:
        if not (10 <= v <= 80):
            raise ValueError("bmi must be between 10 and 80")
        return v

    @field_validator("smoking_status")
    @classmethod
    def validate_smoking_status(cls, v: str) -> str:
        if v not in ("never smoked", "formerly smoked", "smokes", "Unknown"):
            raise ValueError("invalid smoking_status")
        return v


class StrokePredictionResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    prediction_id: uuid.UUID
    risk_level: str
    probability: float
    contributing_factors: list[str]
    model_version: str
    created_at: datetime


class KidneyDiseasePredictionRequest(BaseModel):
    age: float
    bp: float  # blood pressure
    sg: float  # urine specific gravity
    al: float  # albumin (0-5)
    su: float  # sugar (0-5)
    rbc: str  # 'normal' or 'abnormal'
    pc: str  # pus cell: 'normal' or 'abnormal'
    pcc: str  # pus cell clumps: 'present' or 'notpresent'
    ba: str  # bacteria: 'present' or 'notpresent'
    bgr: float  # blood glucose random
    bu: float  # blood urea
    sc: float  # serum creatinine
    sod: float  # sodium
    pot: float  # potassium
    hemo: float  # hemoglobin
    pcv: float  # packed cell volume
    wc: float  # white blood cell count
    rc: float  # red blood cell count
    htn: str  # hypertension: 'yes' or 'no'
    dm: str  # diabetes mellitus: 'yes' or 'no'
    cad: str  # coronary artery disease: 'yes' or 'no'
    appet: str  # appetite: 'good' or 'poor'
    pe: str  # pedal edema: 'yes' or 'no'
    ane: str  # anemia: 'yes' or 'no'

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: float) -> float:
        if not (0 <= v <= 120):
            raise ValueError("age must be between 0 and 120")
        return v

    @field_validator("sg")
    @classmethod
    def validate_sg(cls, v: float) -> float:
        if not (1.000 <= v <= 1.040):
            raise ValueError("sg must be between 1.000 and 1.040")
        return v

    @field_validator("al", "su")
    @classmethod
    def validate_0_to_5(cls, v: float) -> float:
        if not (0 <= v <= 5):
            raise ValueError("must be between 0 and 5")
        return v

    @field_validator("rbc", "pc")
    @classmethod
    def validate_normal_abnormal(cls, v: str) -> str:
        if v not in ("normal", "abnormal"):
            raise ValueError("must be 'normal' or 'abnormal'")
        return v

    @field_validator("pcc", "ba")
    @classmethod
    def validate_present(cls, v: str) -> str:
        if v not in ("present", "notpresent"):
            raise ValueError("must be 'present' or 'notpresent'")
        return v

    @field_validator("htn", "dm", "cad", "pe", "ane")
    @classmethod
    def validate_yes_no(cls, v: str) -> str:
        if v not in ("yes", "no"):
            raise ValueError("must be 'yes' or 'no'")
        return v

    @field_validator("appet")
    @classmethod
    def validate_appet(cls, v: str) -> str:
        if v not in ("good", "poor"):
            raise ValueError("must be 'good' or 'poor'")
        return v


class KidneyDiseasePredictionResponse(BaseModel):
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
