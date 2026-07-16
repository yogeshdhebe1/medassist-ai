import uuid

from sqlalchemy.orm import Session

from app.modules.settings.models import UserSettings


class SettingsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: uuid.UUID) -> UserSettings | None:
        return self.db.query(UserSettings).filter(UserSettings.user_id == user_id).first()

    def create(self, user_id: uuid.UUID) -> UserSettings:
        record = UserSettings(user_id=user_id)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update(self, settings: UserSettings, **fields) -> UserSettings:
        for key, value in fields.items():
            if value is not None:
                setattr(settings, key, value)
        self.db.commit()
        self.db.refresh(settings)
        return settings
