import uuid

from fastapi import APIRouter, Depends, File, UploadFile, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.modules.authentication.models import User
from app.modules.medical_reports.schemas import MedicalReportResponse
from app.modules.medical_reports.services import MedicalReportService

router = APIRouter(prefix="/reports", tags=["Medical Reports"])


@router.post("/upload", response_model=MedicalReportResponse, status_code=201)
async def upload_report(
    file: UploadFile = File(...),
    report_type: str | None = Form(default=None),
    current_user: User = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    service = MedicalReportService(db)
    return await service.upload_report(current_user.id, file, report_type)


@router.get("", response_model=list[MedicalReportResponse])
def list_my_reports(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(require_role("patient")),
    db: Session = Depends(get_db),
):
    service = MedicalReportService(db)
    return service.list_my_reports(current_user.id, page, page_size)


@router.get("/patient/{patient_id}", response_model=list[MedicalReportResponse])
def list_patient_reports(
    patient_id: uuid.UUID,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(require_role("doctor")),
    db: Session = Depends(get_db),
):
    """Lets an assigned doctor view a specific patient's uploaded reports."""
    service = MedicalReportService(db)
    return service.list_patient_reports_as_doctor(current_user.id, patient_id, page, page_size)


@router.get("/{report_id}", response_model=MedicalReportResponse)
def get_report_metadata(
    report_id: uuid.UUID,
    current_user: User = Depends(require_role("patient", "doctor")),
    db: Session = Depends(get_db),
):
    service = MedicalReportService(db)
    return service.get_report(report_id, current_user.id, current_user.role)


@router.get("/{report_id}/download")
def download_report(
    report_id: uuid.UUID,
    current_user: User = Depends(require_role("patient", "doctor")),
    db: Session = Depends(get_db),
):
    service = MedicalReportService(db)
    report = service.get_report(report_id, current_user.id, current_user.role)
    return FileResponse(
        path=report.file_path,
        filename=report.original_filename,
        media_type="application/octet-stream",
    )
