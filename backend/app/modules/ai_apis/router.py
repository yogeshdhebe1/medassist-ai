from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.modules.authentication.models import User
from app.modules.ai_apis.schemas import (
    DiabetesPredictionRequest,
    DiabetesPredictionResponse,
    HeartDiseasePredictionRequest,
    HeartDiseasePredictionResponse,
    StrokePredictionRequest,
    StrokePredictionResponse,
    KidneyDiseasePredictionRequest,
    KidneyDiseasePredictionResponse,
    PredictionHistoryItem,
)
from app.modules.ai_apis.services import AIPredictionService
from app.modules.ai_apis.service_risk_score import HealthRiskScoreService
from app.modules.ai_apis.schemas_risk_score import HealthRiskScoreResponse

router = APIRouter(prefix="/ai", tags=["AI Predictions"])


@router.post("/disease-prediction/diabetes", response_model=DiabetesPredictionResponse)
def predict_diabetes(
    payload: DiabetesPredictionRequest,
    current_user: User = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    service = AIPredictionService(db)
    return service.predict_diabetes_risk(current_user.id, payload)


@router.post("/disease-prediction/heart-disease", response_model=HeartDiseasePredictionResponse)
def predict_heart_disease(
    payload: HeartDiseasePredictionRequest,
    current_user: User = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    service = AIPredictionService(db)
    return service.predict_heart_disease_risk(current_user.id, payload)


@router.post("/disease-prediction/stroke", response_model=StrokePredictionResponse)
def predict_stroke(
    payload: StrokePredictionRequest,
    current_user: User = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    service = AIPredictionService(db)
    return service.predict_stroke_risk(current_user.id, payload)


@router.post("/disease-prediction/kidney-disease", response_model=KidneyDiseasePredictionResponse)
def predict_kidney_disease(
    payload: KidneyDiseasePredictionRequest,
    current_user: User = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    service = AIPredictionService(db)
    return service.predict_kidney_disease_risk(current_user.id, payload)


@router.get("/predictions/history", response_model=list[PredictionHistoryItem])
def get_prediction_history(
    prediction_type: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    service = AIPredictionService(db)
    return service.get_history(current_user.id, prediction_type, page, page_size)


@router.post("/health-risk-score", response_model=HealthRiskScoreResponse)
def calculate_health_risk_score(
    current_user: User = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    """Aggregates the patient's most recent diabetes/heart/stroke/kidney
    predictions into a single overall risk score. Requires at least one
    disease prediction to have been run first."""
    service = HealthRiskScoreService(db)
    return service.calculate(current_user.id)
