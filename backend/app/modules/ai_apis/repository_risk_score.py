import uuid

from sqlalchemy.orm import Session

from app.modules.ai_apis.models_risk_score import HealthRiskScore
from app.modules.ai_apis.models import AIPrediction


class HealthRiskScoreRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_latest_prediction_by_type(self, patient_id: uuid.UUID, prediction_type: str) -> AIPrediction | None:
        return (
            self.db.query(AIPrediction)
            .filter(AIPrediction.patient_id == patient_id, AIPrediction.prediction_type == prediction_type)
            .order_by(AIPrediction.created_at.desc())
            .first()
        )

    def get_latest_score(self, patient_id: uuid.UUID) -> HealthRiskScore | None:
        return (
            self.db.query(HealthRiskScore)
            .filter(HealthRiskScore.patient_id == patient_id)
            .order_by(HealthRiskScore.calculated_at.desc())
            .first()
        )

    def create_score(self, patient_id: uuid.UUID, overall_score: float, component_scores: dict) -> HealthRiskScore:
        record = HealthRiskScore(patient_id=patient_id, overall_score=overall_score, component_scores=component_scores)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record
