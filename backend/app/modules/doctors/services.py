import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.modules.doctors.models import Doctor, PatientNote
from app.modules.doctors.repository import DoctorRepository
from app.modules.doctors.schemas import DoctorProfileUpdateRequest, PatientNoteCreateRequest
from app.modules.patients.models import Patient
from app.modules.patients.repository import PatientRepository


class DoctorService:
    def __init__(self, db: Session):
        self.repo = DoctorRepository(db)
        self.patient_repo = PatientRepository(db)

    def get_or_create_profile(self, user_id: uuid.UUID) -> Doctor:
        doctor = self.repo.get_by_user_id(user_id)
        if not doctor:
            doctor = self.repo.create(user_id)
        return doctor

    def update_profile(self, user_id: uuid.UUID, payload: DoctorProfileUpdateRequest) -> Doctor:
        doctor = self.get_or_create_profile(user_id)
        return self.repo.update(doctor, **payload.model_dump(exclude_unset=True))

    def get_public_profile(self, doctor_id: uuid.UUID) -> Doctor:
        doctor = self.repo.get_by_id(doctor_id)
        if not doctor:
            raise NotFoundError("Doctor not found")
        return doctor

    def list_my_patients(self, doctor_user_id: uuid.UUID, page: int = 1, page_size: int = 20) -> list[Patient]:
        doctor = self.get_or_create_profile(doctor_user_id)
        return self.repo.list_assigned_patients(doctor.id, page, page_size)

    def _assert_assigned(self, doctor: Doctor, patient_id: uuid.UUID) -> None:
        """Core RBAC check: a doctor may only act on patients they are explicitly assigned to
        (per Security Architecture doc - enforced at the service layer, not just the router)."""
        if not self.repo.is_assigned(doctor.id, patient_id):
            raise ForbiddenError("You are not assigned to this patient")

    def add_patient_note(self, doctor_user_id: uuid.UUID, payload: PatientNoteCreateRequest) -> PatientNote:
        doctor = self.get_or_create_profile(doctor_user_id)

        patient = self.patient_repo.get_by_id(payload.patient_id)
        if not patient:
            raise NotFoundError("Patient not found")

        self._assert_assigned(doctor, patient.id)
        return self.repo.create_note(doctor.id, patient.id, payload.note)

    def assign_patient(self, doctor_user_id: uuid.UUID, patient_id: uuid.UUID) -> None:
        """Admin-mediated in production; exposed here as a simple dev/testing helper
        so a doctor<->patient relationship can be created without a full admin module yet."""
        doctor = self.get_or_create_profile(doctor_user_id)

        patient = self.patient_repo.get_by_id(patient_id)
        if not patient:
            raise NotFoundError("Patient not found")

        if not self.repo.is_assigned(doctor.id, patient.id):
            self.repo.assign_patient(doctor.id, patient.id)
