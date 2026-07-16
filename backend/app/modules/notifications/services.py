import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.modules.notifications.models import Notification
from app.modules.notifications.repository import NotificationRepository


class NotificationService:
    def __init__(self, db: Session):
        self.repo = NotificationRepository(db)

    def notify(self, user_id: uuid.UUID, title: str, body: str, type: str = "general") -> Notification:
        """Reusable entry point for OTHER modules to create a notification as a side
        effect of their own actions (e.g. appointments confirming a booking, or
        prescriptions being issued) — see appointments/services.py and
        prescriptions/services.py for where this gets called."""
        return self.repo.create(user_id, title, body, type)

    def list_my_notifications(
        self, user_id: uuid.UUID, unread_only: bool, page: int, page_size: int
    ) -> list[Notification]:
        return self.repo.list_for_user(user_id, unread_only, page, page_size)

    def get_unread_count(self, user_id: uuid.UUID) -> int:
        return self.repo.count_unread(user_id)

    def mark_as_read(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> Notification:
        notification = self.repo.get_by_id(notification_id)
        if not notification:
            raise NotFoundError("Notification not found")
        if notification.user_id != user_id:
            raise ForbiddenError("You do not have access to this notification")
        return self.repo.mark_read(notification)
