import uuid

from sqlalchemy.orm import Session

from app.modules.authentication.models import User


class AdminUserRepository:
    """Admin-facing queries over the `users` table, separate from
    `authentication.repository.UserRepository` (which is auth-flow-specific:
    lookup by email/phone during login/register). This repository is for
    admin listing/management use cases instead."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def list_users(
        self, role: str | None = None, is_active: bool | None = None, search: str | None = None,
        page: int = 1, page_size: int = 20,
    ) -> list[User]:
        query = self.db.query(User)
        if role:
            query = query.filter(User.role == role)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        if search:
            query = query.filter(User.email.ilike(f"%{search}%"))
        return (
            query.order_by(User.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

    def update_status(self, user: User, is_active: bool) -> User:
        user.is_active = is_active
        self.db.commit()
        self.db.refresh(user)
        return user
