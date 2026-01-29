#!/usr/bin/env python3
"""
Создаёт на стаджинге два аккаунта:
  - Премиум-пользователь (подписка developer)
  - Админ (доступ в админку)

Запуск на VPS в папке стаджинг-бэкенда (где .env с DATABASE_URL стаджинга):
  cd /root/matchacalc-backend-staging && .venv/bin/python scripts/create_staging_users.py
"""
import sys
import os
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import User, Subscription, UserRole, SubscriptionPlan, SubscriptionStatus
import bcrypt


PREMIUM_EMAIL = "premium.stagging@commercial.ru"
PREMIUM_PASSWORD = "StagingFacePremium333WWW###"

ADMIN_EMAIL = "admin.stagging@commercial.ru"
ADMIN_PASSWORD = "StagingFaceAdmin333WWW###"

# Подписка премиума до конца 2026
PREMIUM_EXPIRES_AT = datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc)


def _hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def ensure_premium_user(db: Session) -> None:
    user = db.query(User).filter(User.email == PREMIUM_EMAIL).first()
    pw_hash = _hash_password(PREMIUM_PASSWORD)
    if user:
        user.password_hash = pw_hash
        user.role = UserRole.USER
        db.commit()
        db.refresh(user)
        print(f"Обновлён премиум-пользователь: {PREMIUM_EMAIL}")
    else:
        user = User(
            email=PREMIUM_EMAIL,
            password_hash=pw_hash,
            role=UserRole.USER,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Создан премиум-пользователь: {PREMIUM_EMAIL}")

    db.query(Subscription).filter(Subscription.user_id == user.id).delete()
    sub = Subscription(
        user_id=user.id,
        plan=SubscriptionPlan.DEVELOPER,
        started_at=datetime.now(timezone.utc),
        expires_at=PREMIUM_EXPIRES_AT,
        status=SubscriptionStatus.ACTIVE,
    )
    db.add(sub)
    db.commit()
    print(f"  Подписка: developer до {PREMIUM_EXPIRES_AT.strftime('%Y-%m-%d')}")


def ensure_admin_user(db: Session) -> None:
    user = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    pw_hash = _hash_password(ADMIN_PASSWORD)
    if user:
        user.password_hash = pw_hash
        user.role = UserRole.ADMIN
        db.commit()
        print(f"Обновлён админ: {ADMIN_EMAIL}")
    else:
        user = User(
            email=ADMIN_EMAIL,
            password_hash=pw_hash,
            role=UserRole.ADMIN,
        )
        db.add(user)
        db.commit()
        print(f"Создан админ: {ADMIN_EMAIL}")


def main() -> int:
    db: Session = SessionLocal()
    try:
        ensure_premium_user(db)
        ensure_admin_user(db)
        print("\n✅ Готово. Логин на стаджинге:")
        print(f"   Премиум: {PREMIUM_EMAIL} / {PREMIUM_PASSWORD}")
        print(f"   Админка: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        return 0
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
