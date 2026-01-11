from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, get_current_user
from app.domain.services.user_service import UserService
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import UserLogin, TokenResponse, TelegramLinkCodeResponse
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserCreate,
    db: Session = Depends(get_db)
):
    service = UserService(db)
    existing = service.get_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    return service.create_user(payload)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: UserLogin,
    db: Session = Depends(get_db)
):
    service = UserService(db)
    user = service.authenticate(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/telegram-link-code", response_model=TelegramLinkCodeResponse)
async def generate_telegram_link_code(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = UserService(db)
    code, expires_at = service.generate_telegram_link_code(current_user)
    return TelegramLinkCodeResponse(code=code, expires_at=expires_at)
