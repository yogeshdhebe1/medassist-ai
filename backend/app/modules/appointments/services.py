import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.modules.appointments.models import Appointment, AppointmentStatus
from app.modules.appointments.repository import AppointmentRepository
from app.modules.appointments.schemas import AppointmentCreateRequest
from app.modules.doctors.repository import DoctorRepository
from app.modules.patients.repository import PatientRepository


class AppointmentService:
    def __init__(self, db: Session):
        self.repo = AppointmentRepository(db)
        self.patient_repo = PatientRepository(db)
        self.doctor_repo = DoctorRepository(db)

    def book_appointment(self, patient_user_id: uuid.UUID, payload: AppointmentCreateRequest) -> Appointment:
        patient = self.patient_repo.get_by_user_id(patient_user_id)
        if not patient:
            patient = self.patient_repo.create(patient_user_id)

        doctor = self.doctor_repo.get_by_id(payload.doctor_id)
        if not doctor:
            raise NotFoundError("Doctor not found")

        return self.repo.create(patient.id, doctor.id, payload.scheduled_at, payload.reason)

    def _load_and_authorize(self, appointment_id: uuid.UUID, user_id: uuid.UUID, role: str) -> Appointment:
        appointment = self.repo.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundError("Appointment not found")

        if role == "patient":
            patient = self.patient_repo.get_by_user_id(user_id)
            if not patient or appointment.patient_id != patient.id:
                raise ForbiddenError("You do not have access to this appointment")
        elif role == "doctor":
            doctor = self.doctor_repo.get_by_user_id(user_id)
            if not doctor or appointment.doctor_id != doctor.id:
                raise ForbiddenError("You do not have access to this appointment")

        return appointment

    def update_status(self, appointment_id: uuid.UUID, user_id: uuid.UUID, role: str, new_status: str) -> Appointment:
        appointment = self._load_and_authorize(appointment_id, user_id, role)

        status_enum = AppointmentStatus(new_status)
        updated = self.repo.update_status(appointment, status_enum)

        # Confirming an appointment establishes the doctor<->patient relationship,
        # so the doctor gains RBAC-checked access to this patient's records
        # (see the assignment check in the doctors module's services.py).
        if status_enum == AppointmentStatus.confirmed:
            if not self.doctor_repo.is_assigned(updated.doctor_id, updated.patient_id):
                self.doctor_repo.assign_patient(updated.doctor_id, updated.patient_id)

        return updated

    def list_my_appointments(self, user_id: uuid.UUID, role: str, page: int, page_size: int) -> list[Appointment]:
        if role == "patient":
            patient = self.patient_repo.get_by_user_id(user_id)
            if not patient:
                return []
            return self.repo.list_for_patient(patient.id, page, page_size)
        elif role == "doctor":
            doctor = self.doctor_repo.get_by_user_id(user_id)
            if not doctor:
                return []
            return self.repo.list_for_doctor(doctor.id, page, page_size)
        return []
