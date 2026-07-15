import uuid

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.modules.doctors.models import Doctor, DoctorPatientAssignment, PatientNote
from app.modules.patients.models import Patient


class DoctorRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: uuid.UUID) -> Doctor | None:
        return self.db.query(Doctor).filter(Doctor.user_id == user_id).first()

    def get_by_id(self, doctor_id: uuid.UUID) -> Doctor | None:
        return self.db.query(Doctor).filter(Doctor.id == doctor_id).first()

    def create(self, user_id: uuid.UUID) -> Doctor:
        doctor = Doctor(user_id=user_id)
        self.db.add(doctor)
        self.db.commit()
        self.db.refresh(doctor)
        return doctor

    def update(self, doctor: Doctor, **fields) -> Doctor:
        for key, value in fields.items():
            if value is not None:
                setattr(doctor, key, value)
        self.db.commit()
        self.db.refresh(doctor)
        return doctor

    def is_assigned(self, doctor_id: uuid.UUID, patient_id: uuid.UUID) -> bool:
        return (
            self.db.query(DoctorPatientAssignment)
            .filter(
                DoctorPatientAssignment.doctor_id == doctor_id,
                DoctorPatientAssignment.patient_id == patient_id,
            )
            .first()
            is not None
        )

    def assign_patient(self, doctor_id: uuid.UUID, patient_id: uuid.UUID) -> DoctorPatientAssignment:
        assignment = DoctorPatientAssignment(doctor_id=doctor_id, patient_id=patient_id)
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment

    def list_assigned_patients(self, doctor_id: uuid.UUID, page: int = 1, page_size: int = 20) -> list[Patient]:
        return (
            self.db.query(Patient)
            .join(DoctorPatientAssignment, DoctorPatientAssignment.patient_id == Patient.id)
            .filter(DoctorPatientAssignment.doctor_id == doctor_id)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

    def create_note(self, doctor_id: uuid.UUID, patient_id: uuid.UUID, note: str) -> PatientNote:
        record = PatientNote(doctor_id=doctor_id, patient_id=patient_id, note=note)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record
