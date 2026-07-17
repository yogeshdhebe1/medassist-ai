from pydantic import BaseModel, field_validator


class RecommendationRequest(BaseModel):
    goal: str | None = None  # 'weight_loss' | 'maintenance' | 'muscle_gain', optional override

    @field_validator("goal")
    @classmethod
    def validate_goal(cls, v: str | None) -> str | None:
        if v is not None and v not in ("weight_loss", "maintenance", "muscle_gain"):
            raise ValueError("goal must be 'weight_loss', 'maintenance', or 'muscle_gain'")
        return v


class RecommendationResponse(BaseModel):
    title: str
    plan: list[str]
    rationale: str
    disclaimer: str = (
        "This is general lifestyle guidance, not a personalized medical or nutrition "
        "prescription. Consult your doctor or a registered dietitian before making "
        "significant diet or exercise changes, especially with an existing condition."
    )
