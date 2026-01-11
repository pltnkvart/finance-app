from sqlalchemy.orm import Session
from typing import Optional, Tuple
from datetime import datetime, timedelta
import secrets

from app.models.user import User
from app.core.security import verify_password, get_password_hash
from app.schemas.user import UserCreate
from app.core.config import settings


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_telegram_id(self, telegram_user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.telegram_user_id == telegram_user_id).first()

    def create_user(self, user_data: UserCreate) -> User:
        user = User(
            email=user_data.email,
            password_hash=get_password_hash(user_data.password)
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def generate_telegram_link_code(self, user: User) -> Tuple[str, datetime]:
        code = secrets.token_hex(3).upper()
        expires_at = datetime.utcnow() + timedelta(minutes=settings.TELEGRAM_LINK_CODE_EXPIRE_MINUTES)
        user.telegram_link_code = code
        user.telegram_link_code_expires_at = expires_at
        self.db.commit()
        self.db.refresh(user)
        return code, expires_at

    def link_telegram_user(
        self,
        code: str,
        telegram_user_id: str,
        telegram_username: Optional[str]
    ) -> Optional[User]:
        now = datetime.utcnow()
        user = self.db.query(User).filter(
            User.telegram_link_code == code,
            User.telegram_link_code_expires_at.is_not(None),
            User.telegram_link_code_expires_at >= now
        ).first()
        if not user:
            return None

        existing = self.db.query(User).filter(User.telegram_user_id == telegram_user_id).first()
        if existing and existing.id != user.id:
            return None

        user.telegram_user_id = telegram_user_id
        user.telegram_username = telegram_username
        user.telegram_link_code = None
        user.telegram_link_code_expires_at = None
        self.db.commit()
        self.db.refresh(user)
        return user
