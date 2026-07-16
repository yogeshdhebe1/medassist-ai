from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.exceptions import AppException, app_exception_handler
from app.modules.authentication.router import router as auth_router
from app.modules.patients.router import router as patients_router
from app.modules.doctors.router import router as doctors_router
from app.modules.ai_apis.router import router as ai_router
from app.modules.appointments.router import router as appointments_router
from app.modules.medical_reports.router import router as reports_router
from app.modules.prescriptions.router import router as prescriptions_router
from app.modules.notifications.router import router as notifications_router
from app.modules.analytics.router import router as analytics_router
from app.modules.users.router import router as users_router
from app.modules.settings.router import router as settings_router
from app.modules.chat.router import router as chat_router

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
app.include_router(doctors_router, prefix="/v1")
app.include_router(ai_router, prefix="/v1")
app.include_router(appointments_router, prefix="/v1")
app.include_router(reports_router, prefix="/v1")
app.include_router(prescriptions_router, prefix="/v1")
app.include_router(notifications_router, prefix="/v1")
app.include_router(analytics_router, prefix="/v1")
app.include_router(users_router, prefix="/v1")
app.include_router(settings_router, prefix="/v1")
app.include_router(chat_router, prefix="/v1")


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": settings.APP_NAME, "environment": settings.ENVIRONMENT}


# All 13 planned backend modules are now implemented:
# authentication, patients, doctors, ai_apis, appointments, medical_reports,
# prescriptions, notifications, analytics, users, settings, chat, and
# file_upload (covered within medical_reports' upload/download endpoints).
