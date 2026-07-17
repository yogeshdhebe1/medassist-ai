import uuid
from datetime import datetime, timezone

from sqlalchemy import Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class HealthRiskScore(Base):
    """Per the Database Design doc: a meta-layer over the existing disease-prediction
    model outputs, NOT a separately trained model. Each row is a snapshot of the
    patient's aggregated risk at a point in time, enabling trend tracking over
    repeated calculations (see `trend` in the API response)."""
    __tablename__ = "health_risk_scores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    component_scores: Mapped[dict] = mapped_column(JSON, nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
