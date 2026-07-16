from pydantic import BaseModel


class AnalyticsOverviewResponse(BaseModel):
    total_patients: int
    total_doctors: int
    total_appointments: int
    appointments_last_30d: int
    reports_uploaded_last_30d: int
    predictions_issued_last_30d: int
    prescriptions_issued_last_30d: int


class AIModelStats(BaseModel):
    model_config = {"protected_namespaces": ()}

    prediction_type: str
    total_predictions: int
    avg_confidence: float | None
    high_risk_count: int


class AIMonitoringResponse(BaseModel):
    models: list[AIModelStats]
