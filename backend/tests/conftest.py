"""Shared fixtures.

Tests run against a REAL PostgreSQL database (the app uses Postgres-specific
types), never your dev database. Create one first:

    CREATE DATABASE medassist_test;

and point TEST_DATABASE_URL at it. The suite refuses to run unless the
database name contains "test", because it wipes every table between tests.
"""
import os
import uuid
from datetime import datetime, timedelta, timezone

TEST_DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://medassist:medassist@localhost:5432/medassist_test",
)
# Must be set BEFORE the app (and its settings object) is imported.
os.environ["DATABASE_URL"] = TEST_DB_URL

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

if "test" not in TEST_DB_URL.rsplit("/", 1)[-1].lower():
    raise RuntimeError(
        f"Refusing to run: database name in '{TEST_DB_URL}' must contain 'test' "
        "(tests delete all data)."
    )

from app.db.base import Base  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402

# Import every model so Base.metadata knows all tables.
from app.modules.authentication.models import User  # noqa: E402,F401
from app.modules.patients.models import Patient  # noqa: E402,F401
from app.modules.doctors.models import Doctor, DoctorPatientAssignment, PatientNote  # noqa: E402,F401
from app.modules.ai_apis.models import AIPrediction  # noqa: E402,F401
from app.modules.ai_apis.models_risk_score import HealthRiskScore  # noqa: E402,F401
from app.modules.appointments.models import Appointment  # noqa: E402,F401
from app.modules.medical_reports.models import MedicalReport  # noqa: E402,F401
from app.modules.medical_reports.models_analysis import ReportOCRResult, ReportAnalysis  # noqa: E402,F401
from app.modules.prescriptions.models import Prescription  # noqa: E402,F401
from app.modules.notifications.models import Notification  # noqa: E402,F401
from app.modules.settings.models import UserSettings  # noqa: E402,F401
from app.modules.chat.models import ChatSession, ChatMessage  # noqa: E402,F401

PASSWORD = "Str0ng!Pass"


@pytest.fixture(scope="session", autouse=True)
def _schema():
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(autouse=True)
def _clean_db():
    yield
    tables = ", ".join(f'"{t.name}"' for t in Base.metadata.sorted_tables)
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def _make_user(client, role: str, verified: bool = True, email: str | None = None):
    email = email or f"{role}-{uuid.uuid4().hex[:8]}@example.com"
    phone = "9" + str(uuid.uuid4().int)[:9]
    r = client.post("/v1/auth/register", json={"email": email, "phone": phone, "password": PASSWORD})
    assert r.status_code == 201, r.text
    user_id = r.json()["user_id"]
    with SessionLocal() as db:
        user = db.get(User, uuid.UUID(user_id))
        user.is_verified = verified
        user.role = role
        db.commit()
    return {"email": email, "user_id": user_id}


def _login(client, email: str) -> dict:
    r = client.post("/v1/auth/login", json={"email": email, "password": PASSWORD})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture()
def make_user(client):
    """make_user(role) -> dict(email, user_id, headers)"""

    def _factory(role: str = "patient"):
        u = _make_user(client, role)
        u["headers"] = _login(client, u["email"])
        return u

    return _factory


@pytest.fixture()
def patient(make_user):
    return make_user("patient")


@pytest.fixture()
def doctor(make_user, client):
    d = make_user("doctor")
    # creates the doctor profile row
    r = client.get("/v1/doctors/me", headers=d["headers"])
    assert r.status_code == 200, r.text
    d["doctor_id"] = r.json()["id"]
    return d


@pytest.fixture()
def admin(make_user):
    return make_user("admin")


def future_iso(days: int = 3) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


def past_iso(days: int = 3) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
