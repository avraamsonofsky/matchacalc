#!/usr/bin/env python3
"""
Скрипт для загрузки seed данных в БД
"""
import sys
import os

# Добавляем путь к приложению
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.database import SessionLocal
from app.db.seeds import seed_all

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_all(db)
        print("✓ Seed данные успешно загружены")
    except Exception as e:
        print(f"✗ Ошибка при загрузке seed данных: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
