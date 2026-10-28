from typing import Optional
from sqlalchemy.orm import Session
from app.core.errors import AuthenticationError, DuplicateEntityError
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.repositories.user_repo import user_repo
from app.schemas.auth import Token, UserLogin, UserRegister, UserResponse


class AuthService:
    @staticmethod
    def register_user(db: Session, user_in: UserRegister) -> UserResponse:
        # Check duplicate email
        if user_repo.get_by_email(db, user_in.email):
            raise DuplicateEntityError("An account with this email address already exists.")
        
        # Check duplicate username
        if user_repo.get_by_username(db, user_in.username):
            raise DuplicateEntityError("This username is already taken. Please choose another.")

        hashed_password = get_password_hash(user_in.password)
        user = user_repo.create(db, user_in, hashed_password)
        return UserResponse.model_validate(user)

    @staticmethod
    def authenticate_user(db: Session, login_in: UserLogin) -> Token:
        identifier = login_in.username_or_email.strip().lower()
        
        user: Optional[User] = None
        if "@" in identifier:
            user = user_repo.get_by_email(db, identifier)
        if not user:
            user = user_repo.get_by_username(db, identifier)

        if not user or not verify_password(login_in.password, user.hashed_password):
            raise AuthenticationError("Invalid username/email or password.")

        if not user.is_active:
            raise AuthenticationError("Account is inactive. Please contact support.")

        access_token = create_access_token(
            subject=str(user.id),
            extra_claims={"username": user.username, "email": user.email},
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )


auth_service = AuthService()

