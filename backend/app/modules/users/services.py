import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import AppException, NotFoundError
from app.modules.authentication.models import User
from app.modules.users.repository import AdminUserRepository


class SelfLockoutError(AppException):
    def __init__(self):
        super().__init__(400, "SELF_LOCKOUT", "You cannot deactivate your own admin account")


class UserManagementService:
    def __init__(self, db: Session):
        self.repo = AdminUserRepository(db)

    def list_users(self, role: str | None, is_active: bool | None, search: str | None, page: int, page_size: int) -> list[User]:
        return self.repo.list_users(role, is_active, search, page, page_size)

    def update_status(self, target_user_id: uuid.UUID, requesting_admin_id: uuid.UUID, is_active: bool) -> User:
        user = self.repo.get_by_id(target_user_id)
        if not user:
            raise NotFoundError("User not found")

        # Guardrail: an admin should never be able to lock themselves out via this
        # endpoint (a real safety concern for any admin-management feature).
        if user.id == requesting_admin_id and not is_active:
            raise SelfLockoutError()

        return self.repo.update_status(user, is_active)
