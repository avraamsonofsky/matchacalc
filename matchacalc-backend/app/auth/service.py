from sqlalchemy.orm import Session
import bcrypt
from app.db.models import User, Subscription, SubscriptionPlan, SubscriptionStatus
from app.auth.schemas import UserRegister
from datetime import datetime, timedelta


def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    # bcrypt ограничен 72 байтами, обрезаем если нужно
    password_bytes = password.encode('utf-8')[:72]
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    # bcrypt ограничен 72 байтами, обрезаем если нужно
    password_bytes = plain_password.encode('utf-8')[:72]
    return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))


def create_user(db: Session, user_data: UserRegister) -> User:
    """Создание нового пользователя"""
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Создаём подписку по умолчанию (NONE)
    subscription = Subscription(
        user_id=db_user.id,
        plan=SubscriptionPlan.NONE,
        status=SubscriptionStatus.ACTIVE
    )
    db.add(subscription)
    db.commit()
    
    return db_user


def get_user_by_email(db: Session, email: str) -> User | None:
    """Получение пользователя по email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Получение пользователя по ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_subscription(db: Session, user_id: int) -> Subscription | None:
    """Получение активной подписки пользователя"""
    return db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.status == SubscriptionStatus.ACTIVE
    ).first()
