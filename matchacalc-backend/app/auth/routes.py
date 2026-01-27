from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.auth.schemas import UserRegister, UserLogin, Token, UserResponse
from app.auth.service import (
    create_user, get_user_by_email, verify_password, get_user_subscription
)
from app.auth.jwt_handler import create_access_token
from app.auth.dependencies import get_current_user
from app.db.models import SubscriptionStatus
from datetime import timedelta
from app.config import settings

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    # Проверяем, существует ли пользователь
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    # Создаём пользователя
    user = create_user(db, user_data)
    
    # Получаем подписку
    subscription = get_user_subscription(db, user.id)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role.value,
        subscription=subscription,
        created_at=user.created_at
    )


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Вход пользователя"""
    user = get_user_by_email(db, credentials.email)
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создаём токен
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение информации о текущем пользователе"""
    subscription = get_user_subscription(db, current_user.id)
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role.value,
        subscription=subscription,
        created_at=current_user.created_at
    )
