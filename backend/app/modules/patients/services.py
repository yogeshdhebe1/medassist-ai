import uuid

from sqlalchemy.orm import Session

from app.modules.patients.models import Patient
from app.modules.patients.repository import PatientRepository
from app.modules.patients.schemas import PatientProfileUpdateRequest


class PatientService:
    def __init__(self, db: Session):
        self.repo = PatientRepository(db)

    def get_or_create_profile(self, user_id: uuid.UUID) -> Patient:
        """Patients don't have a profile row until they first view/edit it (lazy creation)."""
        patient = self.repo.get_by_user_id(user_id)
        if not patient:
            patient = self.repo.create(user_id)
        return patient

    def update_profile(self, user_id: uuid.UUID, payload: PatientProfileUpdateRequest) -> Patient:
        patient = self.get_or_create_profile(user_id)
        return self.repo.update(patient, **payload.model_dump(exclude_unset=True))
