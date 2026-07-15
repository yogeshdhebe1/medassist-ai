from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.exceptions import AppException, app_exception_handler
from app.modules.authentication.router import router as auth_router
from app.modules.patients.router import router as patients_router

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="MedAssist AI - Core Backend API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, app_exception_handler)

app.include_router(auth_router, prefix="/v1")
app.include_router(patients_router, prefix="/v1")


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": settings.APP_NAME, "environment": settings.ENVIRONMENT}


# Remaining modules (users, doctors, appointments, medical_reports, prescriptions,
# notifications, chat, ai_apis, analytics, file_upload, settings) will each
# register their own router here, following the same pattern as patients_router above.
