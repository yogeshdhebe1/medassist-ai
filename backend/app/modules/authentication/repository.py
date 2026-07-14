from sqlalchemy.orm import Session

from app.modules.authentication.models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_phone(self, phone: str) -> User | None:
        return self.db.query(User).filter(User.phone == phone).first()

    def get_by_id(self, user_id) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, email: str, phone: str, password_hash: str, role: str = "patient") -> User:
        user = User(email=email, phone=phone, password_hash=password_hash, role=role)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def mark_verified(self, user: User) -> User:
        user.is_verified = True
        self.db.commit()
        self.db.refresh(user)
        return user
