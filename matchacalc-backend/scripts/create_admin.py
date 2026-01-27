#!/usr/bin/env python3
"""
Скрипт для создания администратора
Использование:
    python create_admin.py <email> <password>
"""
import sys
import os

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import User, UserRole
import bcrypt

def create_admin(email: str, password: str):
    """Создаёт пользователя с ролью администратора"""
    db: Session = SessionLocal()
    
    try:
        existing_user = db.query(User).filter(User.email == email).first()
        
        # Хешируем пароль
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

        if existing_user:
            print(f"Пользователь {email} уже существует. Назначаем роль ADMIN...")
            existing_user.password_hash = password_hash
            existing_user.role = UserRole.ADMIN
            db.commit()
            print(f"✅ Роль администратора назначена пользователю {email}!")
        else:
            user = User(
                email=email,
                password_hash=password_hash,
                role=UserRole.ADMIN
            )
            db.add(user)
            db.commit()
            print(f"✅ Создан администратор: {email}")
        
        return 0
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {e}")
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Использование:")
        print(f"  {sys.argv[0]} <email> <password>")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    
    exit_code = create_admin(email, password)
    sys.exit(exit_code)
