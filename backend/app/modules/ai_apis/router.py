from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.modules.authentication.models import User
from app.modules.ai_apis.schemas import (
    DiabetesPredictionRequest,
    DiabetesPredictionResponse,
    PredictionHistoryItem,
)
from app.modules.ai_apis.services import AIPredictionService

router = APIRouter(prefix="/ai", tags=["AI Predictions"])


@router.post("/disease-prediction/diabetes", response_model=DiabetesPredictionResponse)
def predict_diabetes(
    payload: DiabetesPredictionRequest,
    current_user: User = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    service = AIPredictionService(db)
    return service.predict_diabetes_risk(current_user.id, payload)


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
