import uuid
from datetime import datetime

from pydantic import BaseModel


class ExtractedField(BaseModel):
    value: float
    unit: str
    display_name: str


class OCRResultResponse(BaseModel):
    id: uuid.UUID
    report_id: uuid.UUID
    extracted_fields: dict[str, ExtractedField]
    confidence_score: float | None
    processed_at: datetime

    class Config:
        from_attributes = True


class AbnormalValueItem(BaseModel):
    test: str
    value: float
    unit: str
    reference_range: str
    flag: str  # 'low' | 'high'


class NormalValueItem(BaseModel):
    test: str
    value: float
    unit: str
    reference_range: str


class ReportAnalysisResponse(BaseModel):
    id: uuid.UUID
    report_id: uuid.UUID
    abnormal_values: list[AbnormalValueItem]
    normal_values: list[NormalValueItem]
    summary: str
    next_steps: str
    analyzed_at: datetime

    class Config:
        from_attributes = True


class AnalyzeReportResponse(BaseModel):
    ocr_result: OCRResultResponse
    analysis: ReportAnalysisResponse
