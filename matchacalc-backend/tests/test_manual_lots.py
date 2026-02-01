import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import get_db, Base
from app.db.models import User, SubscriptionStatus, Subscription, Collection
from datetime import datetime, timedelta
import uuid

# Тестовая БД в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
from sqlalchemy import create_engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def create_test_user_with_sub(db):
    user = User(
        email=f"test_{uuid.uuid4()}@example.com",
        password_hash="hash",
        role="USER"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    sub = Subscription(
        user_id=user.id,
        plan="AGENT",
        status=SubscriptionStatus.ACTIVE,
        expires_at=datetime.now() + timedelta(days=30)
    )
    db.add(sub)
    db.commit()
    return user

def get_token(user_id):
    from app.auth.jwt_handler import create_access_token
    return create_access_token(data={"sub": str(user_id)})

def test_add_lot_manual_success():
    db = TestingSessionLocal()
    user = create_test_user_with_sub(db)
    token = get_token(user.id)
    
    # 1. Создаем коллекцию
    coll_res = client.post(
        "/api/v1/collections/",
        json={"name": "Test Collection", "description": "Desc"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert coll_res.status_code in [200, 201]
    collection_id = coll_res.json()["id"]
    
    # 2. Добавляем лот вручную
    lot_data = {
        "address": "Test Address",
        "purchase_price": 50000000.0,
        "area": 100.0,
        "location_group_id": "center_ttk",
        "rve_date": datetime.now().isoformat(),
        "layout_image_url": "/uploads/test.png",
        "cian_url": "manual_test_123"
    }
    
    response = client.post(
        f"/api/v1/lots/{collection_id}/lots-manual",
        json=lot_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["address"] == "Test Address"
    assert data["purchase_price"] == 50000000.0
    assert data["cian_url"] == "manual_test_123"

def test_add_lot_manual_missing_cian_url():
    """Проверка исправления ошибки 422 (cian_url теперь необязателен)"""
    db = TestingSessionLocal()
    user = create_test_user_with_sub(db)
    token = get_token(user.id)
    
    coll_res = client.post(
        "/api/v1/collections/",
        json={"name": "Test Collection", "description": "Desc"},
        headers={"Authorization": f"Bearer {token}"}
    )
    collection_id = coll_res.json()["id"]
    
    # Данные БЕЗ cian_url
    lot_data = {
        "address": "Test Address No URL",
        "purchase_price": 40000000.0,
        "area": 80.0,
        "location_group_id": "center_ttk",
        "rve_date": datetime.now().isoformat(),
        "layout_image_url": None
    }
    
    response = client.post(
        f"/api/v1/lots/{collection_id}/lots-manual",
        json=lot_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Теперь должно быть 200, а не 422
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["address"] == "Test Address No URL"
    assert data["cian_url"].startswith("manual_")
