import uuid

from sqlalchemy.orm import Session

from app.modules.settings.models import UserSettings
from app.modules.settings.repository import SettingsRepository
from app.modules.settings.schemas import UserSettingsUpdateRequest


class SettingsService:
    def __init__(self, db: Session):
        self.repo = SettingsRepository(db)

    def get_or_create(self, user_id: uuid.UUID) -> UserSettings:
        settings = self.repo.get_by_user_id(user_id)
        if not settings:
            settings = self.repo.create(user_id)
        return settings

    def update(self, user_id: uuid.UUID, payload: UserSettingsUpdateRequest) -> UserSettings:
        settings = self.get_or_create(user_id)
        return self.repo.update(settings, **payload.model_dump(exclude_unset=True))
