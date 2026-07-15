from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base application exception -> maps to a standardized error envelope."""

    def __init__(self, status_code: int, code: str, message: str, details: dict | None = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}


class InvalidCredentialsError(AppException):
    def __init__(self):
        super().__init__(401, "INVALID_CREDENTIALS", "Invalid email or password")


class AccountNotVerifiedError(AppException):
    def __init__(self):
        super().__init__(403, "ACCOUNT_NOT_VERIFIED", "Account has not been verified")


class DuplicateUserError(AppException):
    def __init__(self):
        super().__init__(409, "USER_EXISTS", "An account with this email or phone already exists")


class ForbiddenError(AppException):
    def __init__(self, message: str = "You do not have permission to perform this action"):
        super().__init__(403, "FORBIDDEN", message)


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(404, "NOT_FOUND", message)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
    )
