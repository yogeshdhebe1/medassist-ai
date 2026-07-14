from sqlalchemy.orm import Session

from app.config import settings
from app.core.exceptions import DuplicateUserError, InvalidCredentialsError, AccountNotVerifiedError
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.modules.authentication.repository import UserRepository
from app.modules.authentication.schemas import RegisterRequest, LoginRequest


class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register(self, payload: RegisterRequest):
        if self.repo.get_by_email(payload.email) or self.repo.get_by_phone(payload.phone):
            raise DuplicateUserError()

        user = self.repo.create(
            email=payload.email,
            phone=payload.phone,
            password_hash=hash_password(payload.password),
            role="patient",
        )
        # TODO: trigger OTP generation + delivery (SMS/email provider integration)
        return user

    def login(self, payload: LoginRequest):
        user = self.repo.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.password_hash):
            raise InvalidCredentialsError()
        if not user.is_verified:
            raise AccountNotVerifiedError()

        access_token = create_access_token(subject=str(user.id), role=user.role)
        refresh_token = create_refresh_token(subject=str(user.id))
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "role": user.role,
        }

    def refresh(self, refresh_token: str):
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise InvalidCredentialsError()

        user = self.repo.get_by_id(payload["sub"])
        if not user:
            raise InvalidCredentialsError()

        access_token = create_access_token(subject=str(user.id), role=user.role)
        return {"access_token": access_token, "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60}
