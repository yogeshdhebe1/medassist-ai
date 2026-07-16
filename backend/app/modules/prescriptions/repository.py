import uuid

from sqlalchemy.orm import Session

from app.modules.prescriptions.models import Prescription


class PrescriptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, prescription_id: uuid.UUID) -> Prescription | None:
        return self.db.query(Prescription).filter(Prescription.id == prescription_id).first()

    def create(self, patient_id: uuid.UUID, doctor_id: uuid.UUID, medications: list, notes: str | None) -> Prescription:
        record = Prescription(patient_id=patient_id, doctor_id=doctor_id, medications=medications, notes=notes)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_for_patient(self, patient_id: uuid.UUID, page: int = 1, page_size: int = 20) -> list[Prescription]:
        return (
            self.db.query(Prescription)
            .filter(Prescription.patient_id == patient_id)
            .order_by(Prescription.issued_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
