import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.modules.doctors.repository import DoctorRepository
from app.modules.patients.repository import PatientRepository
from app.modules.prescriptions.models import Prescription
from app.modules.prescriptions.repository import PrescriptionRepository
from app.modules.prescriptions.schemas import PrescriptionCreateRequest


class PrescriptionService:
    def __init__(self, db: Session):
        self.repo = PrescriptionRepository(db)
        self.patient_repo = PatientRepository(db)
        self.doctor_repo = DoctorRepository(db)

    def create_prescription(self, doctor_user_id: uuid.UUID, payload: PrescriptionCreateRequest) -> Prescription:
        doctor = self.doctor_repo.get_by_user_id(doctor_user_id)
        if not doctor:
            doctor = self.doctor_repo.create(doctor_user_id)

        patient = self.patient_repo.get_by_id(payload.patient_id)
        if not patient:
            raise NotFoundError("Patient not found")

        if not self.doctor_repo.is_assigned(doctor.id, patient.id):
            raise ForbiddenError("You are not assigned to this patient")

        medications_dicts = [m.model_dump() for m in payload.medications]
        return self.repo.create(patient.id, doctor.id, medications_dicts, payload.notes)

    def list_for_patient(self, patient_id: uuid.UUID, user_id: uuid.UUID, role: str, page: int, page_size: int) -> list[Prescription]:
        if role == "patient":
            patient = self.patient_repo.get_by_user_id(user_id)
            if not patient or patient.id != patient_id:
                raise ForbiddenError("You do not have access to these prescriptions")
        elif role == "doctor":
            doctor = self.doctor_repo.get_by_user_id(user_id)
            if not doctor or not self.doctor_repo.is_assigned(doctor.id, patient_id):
                raise ForbiddenError("You are not assigned to this patient")

        return self.repo.list_for_patient(patient_id, page, page_size)

    def list_my_prescriptions(self, patient_user_id: uuid.UUID, page: int, page_size: int) -> list[Prescription]:
        patient = self.patient_repo.get_by_user_id(patient_user_id)
        if not patient:
            return []
        return self.repo.list_for_patient(patient.id, page, page_size)
