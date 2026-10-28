from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import Token, UserLogin, UserRegister, UserResponse
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    """Register a new user account."""
    return auth_service.register_user(db, user_in)


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    """Authenticate credentials and generate JWT access token."""
    return auth_service.authenticate_user(db, login_in)


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Retrieve profile of currently authenticated user."""
    return UserResponse.model_validate(current_user)

