import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.modules.doctors.repository import DoctorRepository
from app.modules.medical_reports.analyzer import analyze_extracted_values
from app.modules.medical_reports.ocr_engine import extract_text, extract_structured_values
from app.modules.medical_reports.repository import MedicalReportRepository
from app.modules.medical_reports.repository_analysis import ReportAnalysisRepository
from app.modules.patients.repository import PatientRepository


class ReportAnalysisService:
    def __init__(self, db: Session):
        self.report_repo = MedicalReportRepository(db)
        self.analysis_repo = ReportAnalysisRepository(db)
        self.patient_repo = PatientRepository(db)
        self.doctor_repo = DoctorRepository(db)

    def _authorize(self, report_id: uuid.UUID, user_id: uuid.UUID, role: str):
        report = self.report_repo.get_by_id(report_id)
        if not report:
            raise NotFoundError("Report not found")

        if role == "patient":
            patient = self.patient_repo.get_by_user_id(user_id)
            if not patient or report.patient_id != patient.id:
                raise ForbiddenError("You do not have access to this report")
        elif role == "doctor":
            doctor = self.doctor_repo.get_by_user_id(user_id)
            if not doctor or not self.doctor_repo.is_assigned(doctor.id, report.patient_id):
                raise ForbiddenError("You are not assigned to this patient")

        return report

    def analyze_report(self, report_id: uuid.UUID, user_id: uuid.UUID, role: str) -> dict:
        report = self._authorize(report_id, user_id, role)

        if report.file_type not in ("jpg", "png"):
            raise ForbiddenError(
                f"OCR analysis currently supports image files (JPG/PNG) only; this report is a {report.file_type}."
            )

        raw_text = extract_text(report.file_path)
        ocr_output = extract_structured_values(raw_text)

        ocr_record = self.analysis_repo.upsert_ocr_result(
            report_id=report.id,
            extracted_fields=ocr_output["extracted_fields"],
            raw_text=ocr_output["raw_text"],
            confidence_score=ocr_output["confidence_score"],
        )

        analysis_output = analyze_extracted_values(ocr_output["extracted_fields"])
        analysis_record = self.analysis_repo.upsert_analysis(
            report_id=report.id,
            abnormal_values=analysis_output["abnormal_values"],
            normal_values=analysis_output["normal_values"],
            summary=analysis_output["summary"],
            next_steps=analysis_output["next_steps"],
        )

        return {"ocr_result": ocr_record, "analysis": analysis_record}

    def get_analysis(self, report_id: uuid.UUID, user_id: uuid.UUID, role: str):
        self._authorize(report_id, user_id, role)

        ocr_record = self.analysis_repo.get_ocr_result(report_id)
        analysis_record = self.analysis_repo.get_analysis(report_id)

        if not ocr_record or not analysis_record:
            raise NotFoundError("This report has not been analyzed yet. Call the analyze endpoint first.")

        return {"ocr_result": ocr_record, "analysis": analysis_record}
