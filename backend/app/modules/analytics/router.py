from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.modules.authentication.models import User
from app.modules.analytics.schemas import AnalyticsOverviewResponse, AIMonitoringResponse
from app.modules.analytics.services import AnalyticsService

router = APIRouter(prefix="/admin/analytics", tags=["Analytics (Admin)"])


@router.get("/overview", response_model=AnalyticsOverviewResponse)
def get_overview(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return AnalyticsService(db).get_overview()


@router.get("/ai-monitoring", response_model=AIMonitoringResponse)
def get_ai_monitoring(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return AnalyticsService(db).get_ai_monitoring()
