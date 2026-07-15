import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.modules.authentication.models import User
from app.modules.doctors.schemas import (
    DoctorProfileResponse,
    DoctorPublicProfileResponse,
    DoctorProfileUpdateRequest,
    PatientSummary,
    PatientNoteCreateRequest,
    PatientNoteResponse,
)
from app.modules.doctors.services import DoctorService

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.get("/me", response_model=DoctorProfileResponse)
def get_my_profile(
    current_user: User = Depends(require_role("doctor")),
    db: Session = Depends(get_db),
):
    return DoctorService(db).get_or_create_profile(current_user.id)


@router.put("/me", response_model=DoctorProfileResponse)
def update_my_profile(
    payload: DoctorProfileUpdateRequest,
    current_user: User = Depends(require_role("doctor")),
    db: Session = Depends(get_db),
):
    return DoctorService(db).update_profile(current_user.id, payload)


@router.get("/me/patients", response_model=list[PatientSummary])
def list_my_patients(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(require_role("doctor")),
    db: Session = Depends(get_db),
):
    return DoctorService(db).list_my_patients(current_user.id, page, page_size)


@router.post("/me/patients/{patient_id}/assign", status_code=204)
def assign_patient(
    patient_id: uuid.UUID,
    current_user: User = Depends(require_role("doctor")),
    db: Session = Depends(get_db),
):
    """Dev/testing helper to create a doctor<->patient relationship.
    In production this would be admin-mediated (see API Design doc)."""
    DoctorService(db).assign_patient(current_user.id, patient_id)


@router.post("/me/patient-notes", response_model=PatientNoteResponse, status_code=201)
def add_patient_note(
    payload: PatientNoteCreateRequest,
    current_user: User = Depends(require_role("doctor")),
    db: Session = Depends(get_db),
):
    return DoctorService(db).add_patient_note(current_user.id, payload)


@router.get("/{doctor_id}", response_model=DoctorPublicProfileResponse)
def get_doctor_public_profile(doctor_id: uuid.UUID, db: Session = Depends(get_db)):
    return DoctorService(db).get_public_profile(doctor_id)
