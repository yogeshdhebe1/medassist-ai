import os
import uuid

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.exceptions import AppException, ForbiddenError, NotFoundError
from app.modules.doctors.repository import DoctorRepository
from app.modules.medical_reports.models import MedicalReport
from app.modules.medical_reports.repository import MedicalReportRepository
from app.modules.patients.repository import PatientRepository

ALLOWED_MIME_TYPES = {
    "application/pdf": "pdf",
    "image/jpeg": "jpg",
    "image/png": "png",
}
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB, per the API Design doc

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "uploads", "medical_reports")


class InvalidFileError(AppException):
    def __init__(self, message: str):
        super().__init__(400, "INVALID_FILE", message)


class MedicalReportService:
    def __init__(self, db: Session):
        self.repo = MedicalReportRepository(db)
        self.patient_repo = PatientRepository(db)
        self.doctor_repo = DoctorRepository(db)

    async def upload_report(
        self, patient_user_id: uuid.UUID, file: UploadFile, report_type: str | None
    ) -> MedicalReport:
        if file.content_type not in ALLOWED_MIME_TYPES:
            raise InvalidFileError(
                f"Unsupported file type '{file.content_type}'. Allowed: PDF, JPG, PNG."
            )

        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE_BYTES:
            raise InvalidFileError("File exceeds the 15 MB size limit.")
        if len(contents) == 0:
            raise InvalidFileError("Uploaded file is empty.")

        patient = self.patient_repo.get_by_user_id(patient_user_id)
        if not patient:
            patient = self.patient_repo.create(patient_user_id)

        extension = ALLOWED_MIME_TYPES[file.content_type]
        stored_filename = f"{uuid.uuid4()}.{extension}"

        os.makedirs(UPLOAD_DIR, exist_ok=True)
        stored_path = os.path.join(UPLOAD_DIR, stored_filename)
        with open(stored_path, "wb") as f:
            f.write(contents)

        return self.repo.create(
            patient_id=patient.id,
            file_path=stored_path,
            original_filename=file.filename or stored_filename,
            file_type=extension,
            report_type=report_type,
        )

    def _authorize_access(self, report: MedicalReport, user_id: uuid.UUID, role: str) -> None:
        if role == "patient":
            patient = self.patient_repo.get_by_user_id(user_id)
            if not patient or report.patient_id != patient.id:
                raise ForbiddenError("You do not have access to this report")
        elif role == "doctor":
            doctor = self.doctor_repo.get_by_user_id(user_id)
            if not doctor or not self.doctor_repo.is_assigned(doctor.id, report.patient_id):
                raise ForbiddenError("You are not assigned to this patient")

    def get_report(self, report_id: uuid.UUID, user_id: uuid.UUID, role: str) -> MedicalReport:
        report = self.repo.get_by_id(report_id)
        if not report:
            raise NotFoundError("Report not found")
        self._authorize_access(report, user_id, role)
        return report

    def list_my_reports(self, user_id: uuid.UUID, page: int, page_size: int) -> list[MedicalReport]:
        patient = self.patient_repo.get_by_user_id(user_id)
        if not patient:
            return []
        return self.repo.list_for_patient(patient.id, page, page_size)

    def list_patient_reports_as_doctor(
        self, doctor_user_id: uuid.UUID, patient_id: uuid.UUID, page: int, page_size: int
    ) -> list[MedicalReport]:
        doctor = self.doctor_repo.get_by_user_id(doctor_user_id)
        if not doctor or not self.doctor_repo.is_assigned(doctor.id, patient_id):
            raise ForbiddenError("You are not assigned to this patient")
        return self.repo.list_for_patient(patient_id, page, page_size)
