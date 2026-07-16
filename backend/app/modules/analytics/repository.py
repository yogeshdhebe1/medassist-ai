from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.modules.ai_apis.models import AIPrediction
from app.modules.appointments.models import Appointment
from app.modules.doctors.models import Doctor
from app.modules.medical_reports.models import MedicalReport
from app.modules.patients.models import Patient
from app.modules.prescriptions.models import Prescription


class AnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def _since(self, days: int) -> datetime:
        return datetime.now(timezone.utc) - timedelta(days=days)

    def count_patients(self) -> int:
        return self.db.query(func.count(Patient.id)).scalar() or 0

    def count_doctors(self) -> int:
        return self.db.query(func.count(Doctor.id)).scalar() or 0

    def count_appointments(self) -> int:
        return self.db.query(func.count(Appointment.id)).scalar() or 0

    def count_appointments_since(self, days: int) -> int:
        return (
            self.db.query(func.count(Appointment.id))
            .filter(Appointment.created_at >= self._since(days))
            .scalar()
            or 0
        )

    def count_reports_since(self, days: int) -> int:
        return (
            self.db.query(func.count(MedicalReport.id))
            .filter(MedicalReport.uploaded_at >= self._since(days))
            .scalar()
            or 0
        )

    def count_predictions_since(self, days: int) -> int:
        return (
            self.db.query(func.count(AIPrediction.id))
            .filter(AIPrediction.created_at >= self._since(days))
            .scalar()
            or 0
        )

    def count_prescriptions_since(self, days: int) -> int:
        return (
            self.db.query(func.count(Prescription.id))
            .filter(Prescription.issued_at >= self._since(days))
            .scalar()
            or 0
        )

    def get_predictions_grouped_by_type(self) -> list[AIPrediction]:
        """Fetch all predictions; grouping/aggregation of the JSON output_result field
        (risk_level) is done in Python in the service layer for DB-portability, since
        JSON field queries are backend-specific (Postgres JSONB operators vs SQLite)."""
        return self.db.query(AIPrediction).all()
