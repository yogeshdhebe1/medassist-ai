import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.modules.appointments.models import Appointment, AppointmentStatus


class AppointmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, appointment_id: uuid.UUID) -> Appointment | None:
        return self.db.query(Appointment).filter(Appointment.id == appointment_id).first()

    def create(self, patient_id: uuid.UUID, doctor_id: uuid.UUID, scheduled_at: datetime, reason: str | None) -> Appointment:
        appointment = Appointment(
            patient_id=patient_id, doctor_id=doctor_id, scheduled_at=scheduled_at, reason=reason
        )
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)
        return appointment

    def update_status(self, appointment: Appointment, status: AppointmentStatus) -> Appointment:
        appointment.status = status
        self.db.commit()
        self.db.refresh(appointment)
        return appointment

    def list_for_patient(self, patient_id: uuid.UUID, page: int = 1, page_size: int = 20) -> list[Appointment]:
        return (
            self.db.query(Appointment)
            .filter(Appointment.patient_id == patient_id)
            .order_by(Appointment.scheduled_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

    def list_for_doctor(self, doctor_id: uuid.UUID, page: int = 1, page_size: int = 20) -> list[Appointment]:
        return (
            self.db.query(Appointment)
            .filter(Appointment.doctor_id == doctor_id)
            .order_by(Appointment.scheduled_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
