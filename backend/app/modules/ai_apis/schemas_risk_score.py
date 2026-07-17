import uuid
from datetime import datetime

from pydantic import BaseModel


class HealthRiskScoreResponse(BaseModel):
    score_id: uuid.UUID
    overall_score: float
    component_scores: dict[str, float | None]
    components_available: list[str]
    components_missing: list[str]
    trend: str  # 'improving' | 'stable' | 'worsening' | 'first_calculation'
    calculated_at: datetime
