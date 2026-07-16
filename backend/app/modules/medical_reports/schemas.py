import uuid
from datetime import datetime

from pydantic import BaseModel


class MedicalReportResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    original_filename: str
    file_type: str
    report_type: str | None
    uploaded_at: datetime

    class Config:
        from_attributes = True
