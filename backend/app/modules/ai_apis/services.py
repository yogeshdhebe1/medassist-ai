import uuid

from sqlalchemy.orm import Session

from app.modules.ai_apis.inference import predict_diabetes
from app.modules.ai_apis.inference_heart import predict_heart_disease
from app.modules.ai_apis.repository import AIPredictionRepository
from app.modules.ai_apis.schemas import DiabetesPredictionRequest, HeartDiseasePredictionRequest
from app.modules.patients.repository import PatientRepository


class AIPredictionService:
    def __init__(self, db: Session):
        self.repo = AIPredictionRepository(db)
        self.patient_repo = PatientRepository(db)

    def _get_or_create_patient(self, user_id: uuid.UUID):
        # Lazily create the patient profile if this is their first-ever interaction,
        # consistent with the pattern used in the patients module.
        patient = self.patient_repo.get_by_user_id(user_id)
        if not patient:
            patient = self.patient_repo.create(user_id)
        return patient

    def _persist_and_format(self, patient_id: uuid.UUID, prediction_type: str, input_data: dict, result: dict) -> dict:
        record = self.repo.create(
            patient_id=patient_id,
            prediction_type=prediction_type,
            input_data=input_data,
            output_result=result,
            confidence_score=result["probability"],
            model_version=result["model_version"],
        )
        return {
            "prediction_id": record.id,
            "risk_level": result["risk_level"],
            "probability": result["probability"],
            "contributing_factors": result["contributing_factors"],
            "model_version": result["model_version"],
            "created_at": record.created_at,
        }

    def predict_diabetes_risk(self, user_id: uuid.UUID, payload: DiabetesPredictionRequest):
        patient = self._get_or_create_patient(user_id)
        result = predict_diabetes(**payload.model_dump())
        return self._persist_and_format(patient.id, "diabetes", payload.model_dump(), result)

    def predict_heart_disease_risk(self, user_id: uuid.UUID, payload: HeartDiseasePredictionRequest):
        patient = self._get_or_create_patient(user_id)
        result = predict_heart_disease(**payload.model_dump())
        return self._persist_and_format(patient.id, "heart_disease", payload.model_dump(), result)

    def get_history(self, user_id: uuid.UUID, prediction_type: str | None, page: int, page_size: int):
        patient = self.patient_repo.get_by_user_id(user_id)
        if not patient:
            return []
        return self.repo.list_for_patient(patient.id, prediction_type, page, page_size)
