import uuid

from sqlalchemy.orm import Session

from app.modules.medical_reports.models import MedicalReport


class MedicalReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, report_id: uuid.UUID) -> MedicalReport | None:
        return self.db.query(MedicalReport).filter(MedicalReport.id == report_id).first()

    def create(
        self,
        patient_id: uuid.UUID,
        file_path: str,
        original_filename: str,
        file_type: str,
        report_type: str | None,
    ) -> MedicalReport:
        record = MedicalReport(
            patient_id=patient_id,
            file_path=file_path,
            original_filename=original_filename,
            file_type=file_type,
            report_type=report_type,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_for_patient(self, patient_id: uuid.UUID, page: int = 1, page_size: int = 20) -> list[MedicalReport]:
        return (
            self.db.query(MedicalReport)
            .filter(MedicalReport.patient_id == patient_id)
            .order_by(MedicalReport.uploaded_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
