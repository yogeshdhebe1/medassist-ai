from collections import defaultdict

from sqlalchemy.orm import Session

from app.modules.analytics.repository import AnalyticsRepository


class AnalyticsService:
    def __init__(self, db: Session):
        self.repo = AnalyticsRepository(db)

    def get_overview(self) -> dict:
        return {
            "total_patients": self.repo.count_patients(),
            "total_doctors": self.repo.count_doctors(),
            "total_appointments": self.repo.count_appointments(),
            "appointments_last_30d": self.repo.count_appointments_since(30),
            "reports_uploaded_last_30d": self.repo.count_reports_since(30),
            "predictions_issued_last_30d": self.repo.count_predictions_since(30),
            "prescriptions_issued_last_30d": self.repo.count_prescriptions_since(30),
        }

    def get_ai_monitoring(self) -> dict:
        predictions = self.repo.get_predictions_grouped_by_type()

        grouped: dict[str, list] = defaultdict(list)
        for p in predictions:
            grouped[p.prediction_type].append(p)

        models = []
        for prediction_type, items in grouped.items():
            confidences = [p.confidence_score for p in items if p.confidence_score is not None]
            avg_confidence = round(sum(confidences) / len(confidences), 4) if confidences else None

            high_risk_count = sum(
                1 for p in items if isinstance(p.output_result, dict) and p.output_result.get("risk_level") == "high"
            )

            models.append(
                {
                    "prediction_type": prediction_type,
                    "total_predictions": len(items),
                    "avg_confidence": avg_confidence,
                    "high_risk_count": high_risk_count,
                }
            )

        return {"models": models}
