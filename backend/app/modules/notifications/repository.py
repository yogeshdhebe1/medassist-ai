import uuid

from sqlalchemy.orm import Session

from app.modules.notifications.models import Notification


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, notification_id: uuid.UUID) -> Notification | None:
        return self.db.query(Notification).filter(Notification.id == notification_id).first()

    def create(self, user_id: uuid.UUID, title: str, body: str, type: str = "general") -> Notification:
        record = Notification(user_id=user_id, title=title, body=body, type=type)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_for_user(
        self, user_id: uuid.UUID, unread_only: bool = False, page: int = 1, page_size: int = 20
    ) -> list[Notification]:
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        if unread_only:
            query = query.filter(Notification.is_read == False)  # noqa: E712
        return (
            query.order_by(Notification.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

    def count_unread(self, user_id: uuid.UUID) -> int:
        return (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read == False)  # noqa: E712
            .count()
        )

    def mark_read(self, notification: Notification) -> Notification:
        notification.is_read = True
        self.db.commit()
        self.db.refresh(notification)
        return notification
