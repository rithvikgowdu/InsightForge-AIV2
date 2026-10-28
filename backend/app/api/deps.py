from typing import Generator, Optional
from fastapi import Depends, Header, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.errors import AuthenticationError
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.user_repo import user_repo


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> User:
    """Validate Bearer token and return active authenticated user."""
    if not authorization:
        raise AuthenticationError("Authorization header is missing. Please log in.")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationError("Invalid authorization scheme. Bearer token expected.")

    token = parts[1]
    payload = decode_access_token(token)
    if not payload:
        raise AuthenticationError("Invalid or expired session token. Please log in again.")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AuthenticationError("Token payload is missing subject identifier.")

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise AuthenticationError("Malformed user identifier in token.")

    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise AuthenticationError("User associated with this token does not exist.")

    if not user.is_active:
        raise AuthenticationError("User account has been deactivated.")

    return user

