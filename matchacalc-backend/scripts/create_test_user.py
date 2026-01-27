#!/usr/bin/env python3
"""
Скрипт для создания пользователя с премиум подпиской
Использование:
    python create_test_user.py <email> <password> <expires_at> [plan]
    
    email - email пользователя
    password - пароль
    expires_at - дата окончания подписки в формате YYYY-MM-DD или YYYY-MM-DD HH:MM:SS
    plan - план подписки: agent (по умолчанию) или developer
"""
import sys
import os
from datetime import datetime, timedelta, timezone

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import User, Subscription, UserRole, SubscriptionPlan, SubscriptionStatus
import bcrypt

def create_test_user(email: str, password: str, expires_at_str: str, plan: str = "agent"):
    """Создаёт пользователя с премиум подпиской"""
    db: Session = SessionLocal()
    
    try:
        # Парсим дату окончания
        try:
            expires_at = datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                expires_at = datetime.strptime(expires_at_str, "%Y-%m-%d")
            except ValueError:
                print(f"❌ Неверный формат даты: {expires_at_str}")
                print("Используйте формат: YYYY-MM-DD или YYYY-MM-DD HH:MM:SS")
                return 1
        
        # Добавляем timezone, если не указан
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        # Определяем план подписки
        if plan.lower() == "developer":
            subscription_plan = SubscriptionPlan.DEVELOPER
            plan_name = "Developer (Застройщик)"
        else:
            subscription_plan = SubscriptionPlan.AGENT
            plan_name = "Pro (Agent)"
        
        # Проверяем, существует ли пользователь
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"Пользователь {email} уже существует. Обновляем пароль и подписку...")
            user = existing_user
            # Обновляем пароль (bcrypt ограничен 72 байтами)
            password_bytes = password.encode('utf-8')
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
            user.password_hash = password_hash
            db.commit()
            db.refresh(user)
        else:
            # Создаём пользователя
            # Хешируем пароль напрямую через bcrypt (bcrypt ограничен 72 байтами)
            password_bytes = password.encode('utf-8')
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
            
            user = User(
                email=email,
                password_hash=password_hash,
                role=UserRole.USER
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Создан пользователь: {email}")
        
        # Удаляем старые подписки пользователя
        db.query(Subscription).filter(Subscription.user_id == user.id).delete()
        
        # Создаём активную подписку
        subscription = Subscription(
            user_id=user.id,
            plan=subscription_plan,
            started_at=datetime.now(timezone.utc),
            expires_at=expires_at,
            status=SubscriptionStatus.ACTIVE
        )
        db.add(subscription)
        db.commit()
        
        print(f"\n✅ Пользователь создан/обновлён!")
        print(f"📧 Email: {email}")
        print(f"🔑 Пароль: {password}")
        print(f"💎 Подписка: {plan_name}")
        print(f"📅 Действует до: {expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
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
    if len(sys.argv) < 4:
        print("Использование:")
        print(f"  {sys.argv[0]} <email> <password> <expires_at> [plan]")
        print("\nПараметры:")
        print("  email       - email пользователя")
        print("  password    - пароль")
        print("  expires_at  - дата окончания подписки (YYYY-MM-DD или YYYY-MM-DD HH:MM:SS)")
        print("  plan        - план подписки: agent (по умолчанию) или developer")
        print("\nПримеры:")
        print(f"  {sys.argv[0]} user@example.com mypassword123 2026-12-31")
        print(f"  {sys.argv[0]} user@example.com mypassword123 '2026-12-31 23:59:59' developer")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    expires_at = sys.argv[3]
    plan = sys.argv[4] if len(sys.argv) > 4 else "agent"
    
    exit_code = create_test_user(email, password, expires_at, plan)
    sys.exit(exit_code)
