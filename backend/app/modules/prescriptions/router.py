import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.modules.authentication.models import User
from app.modules.prescriptions.schemas import PrescriptionCreateRequest, PrescriptionResponse
from app.modules.prescriptions.services import PrescriptionService

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])


@router.post("", response_model=PrescriptionResponse, status_code=201)
def create_prescription(
    payload: PrescriptionCreateRequest,
    current_user: User = Depends(require_role("doctor")),
    db: Session = Depends(get_db),
):
    return PrescriptionService(db).create_prescription(current_user.id, payload)


@router.get("/me", response_model=list[PrescriptionResponse])
def list_my_prescriptions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    return PrescriptionService(db).list_my_prescriptions(current_user.id, page, page_size)


@router.get("/patient/{patient_id}", response_model=list[PrescriptionResponse])
def list_patient_prescriptions(
    patient_id: uuid.UUID,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(require_role("patient", "doctor")),
    db: Session = Depends(get_db),
):
    return PrescriptionService(db).list_for_patient(patient_id, current_user.id, current_user.role, page, page_size)
