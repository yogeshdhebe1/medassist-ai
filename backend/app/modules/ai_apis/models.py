import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class AIPrediction(Base):
    """Generic table for all AI/ML prediction modules (per Database Design doc) -
    `prediction_type` discriminates which module produced the result (e.g. 'diabetes'),
    avoiding a separate table per disease as more AI modules are added."""
    __tablename__ = "ai_predictions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    prediction_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    input_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    output_result: Mapped[dict] = mapped_column(JSON, nullable=False)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
