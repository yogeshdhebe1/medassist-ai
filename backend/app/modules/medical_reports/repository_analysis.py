import uuid

from sqlalchemy.orm import Session

from app.modules.medical_reports.models_analysis import ReportOCRResult, ReportAnalysis


class ReportAnalysisRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_ocr_result(self, report_id: uuid.UUID) -> ReportOCRResult | None:
        return self.db.query(ReportOCRResult).filter(ReportOCRResult.report_id == report_id).first()

    def get_analysis(self, report_id: uuid.UUID) -> ReportAnalysis | None:
        return self.db.query(ReportAnalysis).filter(ReportAnalysis.report_id == report_id).first()

    def upsert_ocr_result(self, report_id: uuid.UUID, extracted_fields: dict, raw_text: str, confidence_score: float) -> ReportOCRResult:
        existing = self.get_ocr_result(report_id)
        if existing:
            existing.extracted_fields = extracted_fields
            existing.raw_text = raw_text
            existing.confidence_score = confidence_score
            self.db.commit()
            self.db.refresh(existing)
            return existing

        record = ReportOCRResult(
            report_id=report_id,
            extracted_fields=extracted_fields,
            raw_text=raw_text,
            confidence_score=confidence_score,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def upsert_analysis(
        self, report_id: uuid.UUID, abnormal_values: list, normal_values: list, summary: str, next_steps: str
    ) -> ReportAnalysis:
        existing = self.get_analysis(report_id)
        if existing:
            existing.abnormal_values = abnormal_values
            existing.normal_values = normal_values
            existing.summary = summary
            existing.next_steps = next_steps
            self.db.commit()
            self.db.refresh(existing)
            return existing

        record = ReportAnalysis(
            report_id=report_id,
            abnormal_values=abnormal_values,
            normal_values=normal_values,
            summary=summary,
            next_steps=next_steps,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record
