import uuid

from sqlalchemy.orm import Session

from app.modules.patients.models import Patient


class PatientRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: uuid.UUID) -> Patient | None:
        return self.db.query(Patient).filter(Patient.user_id == user_id).first()

    def get_by_id(self, patient_id: uuid.UUID) -> Patient | None:
        return self.db.query(Patient).filter(Patient.id == patient_id).first()

    def create(self, user_id: uuid.UUID) -> Patient:
        patient = Patient(user_id=user_id)
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        return patient

    def update(self, patient: Patient, **fields) -> Patient:
        for key, value in fields.items():
            if value is not None:
                setattr(patient, key, value)
        self.db.commit()
        self.db.refresh(patient)
        return patient
