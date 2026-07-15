from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.exceptions import InvalidCredentialsError, ForbiddenError
from app.core.security import decode_token
from app.db.session import get_db
from app.modules.authentication.models import User
from app.modules.authentication.repository import UserRepository

# HTTPBearer registers a proper "Authorize" lock button in Swagger UI (/docs),
# and Swagger will automatically attach the "Authorization: Bearer <token>"
# header to every subsequent request once you authorize once.
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Extracts and validates the bearer token, returning the authenticated User.

    Raises InvalidCredentialsError (401) if the token is missing, invalid, or the user no longer exists.
    """
    if not credentials or not credentials.credentials:
        raise InvalidCredentialsError()

    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        raise InvalidCredentialsError()

    user = UserRepository(db).get_by_id(payload["sub"])
    if not user or not user.is_active:
        raise InvalidCredentialsError()

    return user


def require_role(*allowed_roles: str):
    """Dependency factory: restricts an endpoint to specific user roles."""

    def _check(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise ForbiddenError(f"This action requires one of the following roles: {', '.join(allowed_roles)}")
        return user

    return _check
