import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.modules.authentication.models import User
from app.modules.users.schemas import UserSummaryResponse, UserStatusUpdateRequest
from app.modules.users.services import UserManagementService

router = APIRouter(prefix="/admin/users", tags=["Users (Admin)"])


@router.get("", response_model=list[UserSummaryResponse])
def list_users(
    role: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return UserManagementService(db).list_users(role, is_active, search, page, page_size)


@router.patch("/{user_id}/status", response_model=UserSummaryResponse)
def update_user_status(
    user_id: uuid.UUID,
    payload: UserStatusUpdateRequest,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return UserManagementService(db).update_status(user_id, current_user.id, payload.is_active)
