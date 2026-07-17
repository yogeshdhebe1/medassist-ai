import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.modules.ai_apis.repository_risk_score import HealthRiskScoreRepository
from app.modules.patients.repository import PatientRepository

# Maps each disease-prediction type to the health-risk-score "component" name
# used in the API response, per the Database Design doc's component_scores shape.
COMPONENT_MAP = {
    "heart_disease": "cardiac",
    "diabetes": "metabolic",
    "kidney_disease": "renal",
    "stroke": "cerebrovascular",
}

# Equal weighting by default (documented in the AI Pipeline doc as "tunable per
# admin configuration" for a future iteration - kept equal and transparent here
# rather than inventing unsourced clinical severity weights).
COMPONENT_WEIGHT = 1.0 / len(COMPONENT_MAP)


class NoDiseasePredictionsError(AppException):
    def __init__(self):
        super().__init__(
            400,
            "NO_PREDICTIONS_AVAILABLE",
            "Run at least one disease prediction (diabetes, heart disease, stroke, or "
            "kidney disease) before requesting a health risk score.",
        )


class HealthRiskScoreService:
    def __init__(self, db: Session):
        self.repo = HealthRiskScoreRepository(db)
        self.patient_repo = PatientRepository(db)

    def calculate(self, user_id: uuid.UUID) -> dict:
        patient = self.patient_repo.get_by_user_id(user_id)
        if not patient:
            patient = self.patient_repo.create(user_id)

        component_scores: dict[str, float | None] = {}
        components_available = []
        components_missing = []

        for prediction_type, component_name in COMPONENT_MAP.items():
            latest = self.repo.get_latest_prediction_by_type(patient.id, prediction_type)
            if latest and latest.confidence_score is not None:
                component_scores[component_name] = round(latest.confidence_score * 100, 1)
                components_available.append(component_name)
            else:
                component_scores[component_name] = None
                components_missing.append(component_name)

        if not components_available:
            raise NoDiseasePredictionsError()

        # Graceful degradation (per AI Pipeline doc): compute the weighted average
        # only over available components, re-normalizing weights so missing
        # components don't silently drag the score toward zero.
        available_values = [component_scores[c] for c in components_available]
        overall_score = round(sum(available_values) / len(available_values), 1)

        previous = self.repo.get_latest_score(patient.id)
        if previous is None:
            trend = "first_calculation"
        elif overall_score > previous.overall_score + 2:
            trend = "worsening"
        elif overall_score < previous.overall_score - 2:
            trend = "improving"
        else:
            trend = "stable"

        record = self.repo.create_score(patient.id, overall_score, component_scores)

        return {
            "score_id": record.id,
            "overall_score": overall_score,
            "component_scores": component_scores,
            "components_available": components_available,
            "components_missing": components_missing,
            "trend": trend,
            "calculated_at": record.calculated_at,
        }
