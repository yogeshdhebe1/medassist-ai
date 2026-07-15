import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_role, get_current_user
from app.db.session import get_db
from app.modules.authentication.models import User
from app.modules.appointments.schemas import (
    AppointmentCreateRequest,
    AppointmentStatusUpdateRequest,
    AppointmentResponse,
)
from app.modules.appointments.services import AppointmentService

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.post("", response_model=AppointmentResponse, status_code=201)
def book_appointment(
    payload: AppointmentCreateRequest,
    current_user: User = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    return AppointmentService(db).book_appointment(current_user.id, payload)


@router.get("", response_model=list[AppointmentResponse])
def list_my_appointments(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(require_role("patient", "doctor")),
    db: Session = Depends(get_db),
):
    return AppointmentService(db).list_my_appointments(current_user.id, current_user.role, page, page_size)


@router.patch("/{appointment_id}/status", response_model=AppointmentResponse)
def update_appointment_status(
    appointment_id: uuid.UUID,
    payload: AppointmentStatusUpdateRequest,
    current_user: User = Depends(require_role("patient", "doctor")),
    db: Session = Depends(get_db),
):
    return AppointmentService(db).update_status(
        appointment_id, current_user.id, current_user.role, payload.status
    )
