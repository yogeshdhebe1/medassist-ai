from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.modules.authentication.models import User
from app.modules.patients.schemas import PatientProfileResponse, PatientProfileUpdateRequest
from app.modules.patients.services import PatientService

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("/me", response_model=PatientProfileResponse)
def get_my_profile(
    current_user: User = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    service = PatientService(db)
    return service.get_or_create_profile(current_user.id)


@router.put("/me", response_model=PatientProfileResponse)
def update_my_profile(
    payload: PatientProfileUpdateRequest,
    current_user: User = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    service = PatientService(db)
    return service.update_profile(current_user.id, payload)
