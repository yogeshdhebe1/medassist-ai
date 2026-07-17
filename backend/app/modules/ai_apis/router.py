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
from app.modules.ai_apis.service_symptom import SymptomCheckerService
from app.modules.ai_apis.schemas_symptom import (
    SymptomCheckerRequest,
    SymptomCheckerResponse,
    KnownSymptomsResponse,
)
from app.modules.ai_apis.service_recommendation import RecommendationService
from app.modules.ai_apis.schemas_recommendation import RecommendationRequest, RecommendationResponse

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


@router.get("/symptom-checker/symptoms", response_model=KnownSymptomsResponse)
def list_known_symptoms(db: Session = Depends(get_db)):
    """Returns the vocabulary of symptom names the symptom checker model
    understands - use this to build a symptom checklist/autocomplete rather
    than guessing valid symptom strings."""
    service = SymptomCheckerService(db)
    return service.list_known_symptoms()


@router.post("/symptom-checker", response_model=SymptomCheckerResponse)
def check_symptoms(
    payload: SymptomCheckerRequest,
    current_user: User = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    service = SymptomCheckerService(db)
    return service.check_symptoms(current_user.id, payload)


@router.post("/recommendations/diet", response_model=RecommendationResponse)
def get_diet_recommendation(
    payload: RecommendationRequest = RecommendationRequest(),
    current_user: User = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    service = RecommendationService(db)
    return service.get_diet_recommendation(current_user.id, payload.goal)


@router.post("/recommendations/exercise", response_model=RecommendationResponse)
def get_exercise_recommendation(
    payload: RecommendationRequest = RecommendationRequest(),
    current_user: User = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    service = RecommendationService(db)
    return service.get_exercise_recommendation(current_user.id, payload.goal)
