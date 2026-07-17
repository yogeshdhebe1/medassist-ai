import uuid

from sqlalchemy.orm import Session

from app.modules.ai_apis.inference_symptom import predict_disease, get_known_symptoms
from app.modules.ai_apis.repository import AIPredictionRepository
from app.modules.ai_apis.schemas_symptom import SymptomCheckerRequest
from app.modules.patients.repository import PatientRepository


class SymptomCheckerService:
    def __init__(self, db: Session):
        self.repo = AIPredictionRepository(db)
        self.patient_repo = PatientRepository(db)

    def check_symptoms(self, user_id: uuid.UUID, payload: SymptomCheckerRequest) -> dict:
        patient = self.patient_repo.get_by_user_id(user_id)
        if not patient:
            patient = self.patient_repo.create(user_id)

        result = predict_disease(payload.symptoms)

        # Persisted in the same generic ai_predictions table as the disease
        # models, with confidence_score set to the top prediction's confidence -
        # keeps this consistent with every other AI module's audit trail.
        top_confidence = result["predictions"][0]["confidence"] if result["predictions"] else None
        record = self.repo.create(
            patient_id=patient.id,
            prediction_type="symptom_checker",
            input_data={"symptoms": payload.symptoms},
            output_result=result,
            confidence_score=top_confidence,
            model_version=result["model_version"],
        )

        return {
            "prediction_id": record.id,
            "predictions": result["predictions"],
            "recommend_doctor_visit": result["recommend_doctor_visit"],
            "recognized_symptoms": result["recognized_symptoms"],
            "unrecognized_symptoms": result["unrecognized_symptoms"],
            "model_version": result["model_version"],
            "created_at": record.created_at,
        }

    def list_known_symptoms(self) -> dict:
        symptoms = get_known_symptoms()
        return {"symptoms": sorted(symptoms), "count": len(symptoms)}
