from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.auth import UserRegister


class UserRepository:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.scalar(select(User).where(User.id == user_id))

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.scalar(select(User).where(User.email == email.lower().strip()))

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        return db.scalar(select(User).where(User.username == username.lower().strip()))

    @staticmethod
    def create(db: Session, user_in: UserRegister, hashed_password: str) -> User:
        user = User(
            email=user_in.email.lower().strip(),
            username=user_in.username.lower().strip(),
            hashed_password=hashed_password,
            full_name=user_in.full_name.strip() if user_in.full_name else None,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


user_repo = UserRepository()

