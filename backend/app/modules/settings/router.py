from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.modules.authentication.models import User
from app.modules.settings.schemas import UserSettingsResponse, UserSettingsUpdateRequest
from app.modules.settings.services import SettingsService

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("/me", response_model=UserSettingsResponse)
def get_my_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SettingsService(db).get_or_create(current_user.id)


@router.put("/me", response_model=UserSettingsResponse)
def update_my_settings(
    payload: UserSettingsUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SettingsService(db).update(current_user.id, payload)
