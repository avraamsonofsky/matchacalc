"""
Seed данные для начальной загрузки
"""
from sqlalchemy.orm import Session
from app.db.models import LocationGroup, ScenarioConfig, User, UserRole, Subscription, SubscriptionPlan, SubscriptionStatus
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed_location_groups(db: Session):
    """Создание групп локаций"""
    groups = [
        {"id": "moscow_city", "name": "Москва-Сити", "description": "Премиум локация"},
        {"id": "big_city", "name": "Большой Сити", "description": "Апскейл локация"},
        {"id": "center_ttk", "name": "Центр внутри ТТК", "description": "Центральная локация"},
        {"id": "mkad_outside_ttk", "name": "Внутри МКАД вне ТТК", "description": "Периферийная локация"},
        {"id": "outside_mkad", "name": "За МКАД", "description": "Удалённая локация"},
    ]
    
    for group_data in groups:
        existing = db.query(LocationGroup).filter(LocationGroup.id == group_data["id"]).first()
        if not existing:
            group = LocationGroup(**group_data)
            db.add(group)
    
    db.commit()
    print("✓ Location groups seeded")


def seed_scenarios(db: Session):
    """Создание сценариев"""
    scenarios = [
        {
            "id": "pes",
            "name": "Пессимистичный",
            "rent_growth_multiplier": 0.8,
            "price_growth_multiplier": 0.8
        },
        {
            "id": "base",
            "name": "Базовый",
            "rent_growth_multiplier": 1.0,
            "price_growth_multiplier": 1.0
        },
        {
            "id": "opt",
            "name": "Оптимистичный",
            "rent_growth_multiplier": 1.2,
            "price_growth_multiplier": 1.2
        },
    ]
    
    for scenario_data in scenarios:
        existing = db.query(ScenarioConfig).filter(ScenarioConfig.id == scenario_data["id"]).first()
        if not existing:
            scenario = ScenarioConfig(**scenario_data)
            db.add(scenario)
    
    db.commit()
    print("✓ Scenarios seeded")


def seed_admin_user(db: Session):
    """Создание администратора по умолчанию"""
    admin_email = "admin@matchacalc.ru"
    admin_password = "admin123"  # В продакшене изменить!
    
    existing = db.query(User).filter(User.email == admin_email).first()
    if not existing:
        admin = User(
            email=admin_email,
            password_hash=pwd_context.hash(admin_password),
            role=UserRole.ADMIN
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        # Создаём подписку для админа
        subscription = Subscription(
            user_id=admin.id,
            plan=SubscriptionPlan.DEVELOPER,
            status=SubscriptionStatus.ACTIVE
        )
        db.add(subscription)
        db.commit()
        print(f"✓ Admin user created: {admin_email} / {admin_password}")
    else:
        print("✓ Admin user already exists")


def seed_all(db: Session):
    """Загрузка всех seed данных"""
    seed_location_groups(db)
    seed_scenarios(db)
    seed_admin_user(db)
    print("✓ All seeds completed")
