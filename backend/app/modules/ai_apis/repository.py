import uuid

from sqlalchemy.orm import Session

from app.modules.ai_apis.models import AIPrediction


class AIPredictionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        patient_id: uuid.UUID,
        prediction_type: str,
        input_data: dict,
        output_result: dict,
        confidence_score: float | None,
        model_version: str,
    ) -> AIPrediction:
        record = AIPrediction(
            patient_id=patient_id,
            prediction_type=prediction_type,
            input_data=input_data,
            output_result=output_result,
            confidence_score=confidence_score,
            model_version=model_version,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_for_patient(
        self, patient_id: uuid.UUID, prediction_type: str | None = None, page: int = 1, page_size: int = 20
    ) -> list[AIPrediction]:
        query = self.db.query(AIPrediction).filter(AIPrediction.patient_id == patient_id)
        if prediction_type:
            query = query.filter(AIPrediction.prediction_type == prediction_type)
        return (
            query.order_by(AIPrediction.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
