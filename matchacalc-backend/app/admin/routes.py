from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models import MarketReport, MarketReportValue, LocationGroup, ScenarioConfig, UserRole
from app.admin.schemas import (
    MarketReportCreate, MarketReportValueCreate, LocationGroupCreate, ScenarioConfigCreate,
    MarketReportResponse, MarketReportValueResponse,
    MarketReportUpdate, MarketReportValueUpdate, LocationGroupUpdate, ScenarioConfigUpdate
)
from app.reports.schemas import LocationGroupResponse, ScenarioResponse
from app.auth.dependencies import get_current_user

router = APIRouter()


def require_admin(current_user=Depends(get_current_user)):
    """Проверка прав администратора"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора"
        )
    return current_user


# Market Reports
@router.get("/reports", response_model=List[MarketReportResponse])
def get_all_reports(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Получение всех отчётов (включая неактивные)"""
    return db.query(MarketReport).order_by(MarketReport.created_at.desc()).all()


@router.post("/reports", response_model=MarketReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(
    report_data: MarketReportCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Создание нового отчёта"""
    report = MarketReport(**report_data.model_dump())
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.put("/reports/{report_id}", response_model=MarketReportResponse)
def update_report(
    report_id: int,
    report_data: MarketReportUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Обновление отчёта"""
    report = db.query(MarketReport).filter(MarketReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Отчёт не найден")
    
    for key, value in report_data.model_dump(exclude_unset=True).items():
        setattr(report, key, value)
    
    db.commit()
    db.refresh(report)
    return report


@router.get("/reports/{report_id}/values", response_model=list[MarketReportValueResponse])
def get_report_values(
    report_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Получение значений отчёта"""
    values = db.query(MarketReportValue).filter(
        MarketReportValue.report_id == report_id
    ).all()
    return values


# Market Report Values
@router.post("/report-values", response_model=MarketReportValueResponse, status_code=status.HTTP_201_CREATED)
def create_report_value(
    value_data: MarketReportValueCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Создание значения отчёта"""
    value = MarketReportValue(**value_data.model_dump())
    db.add(value)
    db.commit()
    db.refresh(value)
    return value


@router.put("/report-values/{value_id}", response_model=MarketReportValueResponse)
def update_report_value(
    value_id: int,
    value_data: MarketReportValueUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Обновление значения отчёта"""
    value = db.query(MarketReportValue).filter(MarketReportValue.id == value_id).first()
    if not value:
        raise HTTPException(status_code=404, detail="Значение не найдено")
    
    for key, val in value_data.model_dump(exclude_unset=True).items():
        setattr(value, key, val)
    
    db.commit()
    db.refresh(value)
    return value


# Location Groups
@router.post("/location-groups", response_model=LocationGroupResponse, status_code=status.HTTP_201_CREATED)
def create_location_group(
    group_data: LocationGroupCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Создание группы локаций"""
    group = LocationGroup(**group_data.model_dump())
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


# Scenario Configs
@router.post("/scenarios", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
def create_scenario(
    scenario_data: ScenarioConfigCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Создание сценария"""
    scenario = ScenarioConfig(**scenario_data.model_dump())
    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    return scenario


@router.put("/scenarios/{scenario_id}", response_model=ScenarioResponse)
def update_scenario(
    scenario_id: str,
    scenario_data: ScenarioConfigUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Обновление сценария"""
    scenario = db.query(ScenarioConfig).filter(ScenarioConfig.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Сценарий не найден")
    
    for key, value in scenario_data.model_dump(exclude_unset=True).items():
        setattr(scenario, key, value)
    
    db.commit()
    db.refresh(scenario)
    return scenario


# JSON Upload
from app.admin.schemas import MarketReportInJson

@router.post("/upload-json", status_code=status.HTTP_200_OK)
def upload_market_data_json(
    reports: List[MarketReportInJson],
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """
    Загрузка данных рынка из JSON.
    Формат: массив отчётов, каждый с массивом values.
    Если отчёт (provider + period) уже существует — обновляет значения.
    """
    created_reports = 0
    updated_reports = 0
    created_values = 0
    updated_values = 0

    for report_data in reports:
        # Ищем существующий отчёт
        existing_report = db.query(MarketReport).filter(
            MarketReport.provider == report_data.provider,
            MarketReport.period == report_data.period
        ).first()

        if existing_report:
            report = existing_report
            # Обновляем поля отчёта
            report.title = report_data.title
            report.file_url = report_data.file_url
            report.active = report_data.active
            updated_reports += 1
        else:
            report = MarketReport(
                provider=report_data.provider,
                title=report_data.title,
                period=report_data.period,
                file_url=report_data.file_url,
                active=report_data.active
            )
            db.add(report)
            db.commit()
            db.refresh(report)
            created_reports += 1

        # Обрабатываем values
        for val in report_data.values:
            try:
                prop_class = PropertyClass(val.property_class)
            except ValueError:
                continue  # Пропускаем некорректный класс

            existing_value = db.query(MarketReportValue).filter(
                MarketReportValue.report_id == report.id,
                MarketReportValue.location_group_id == val.location_group_id,
                MarketReportValue.property_class == prop_class
            ).first()

            if existing_value:
                existing_value.rent_start = val.rent_start
                existing_value.rent_growth_annual = val.rent_growth_annual
                existing_value.price_per_m2_start = val.price_per_m2_start
                existing_value.price_growth_annual = val.price_growth_annual
                existing_value.vacancy_rate = val.vacancy_rate
                updated_values += 1
            else:
                new_value = MarketReportValue(
                    report_id=report.id,
                    location_group_id=val.location_group_id,
                    property_class=prop_class,
                    rent_start=val.rent_start,
                    rent_growth_annual=val.rent_growth_annual,
                    price_per_m2_start=val.price_per_m2_start,
                    price_growth_annual=val.price_growth_annual,
                    vacancy_rate=val.vacancy_rate
                )
                db.add(new_value)
                created_values += 1

        db.commit()

    return {
        "message": "Данные загружены",
        "created_reports": created_reports,
        "updated_reports": updated_reports,
        "created_values": created_values,
        "updated_values": updated_values
    }


# User Management
from app.db.models import User, Subscription, SubscriptionPlan, SubscriptionStatus
from app.admin.schemas import UserResponse, UserCreate, UserUpdate
from app.auth.service import get_password_hash


@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Получить список всех пользователей с подписками"""
    users = db.query(User).order_by(User.created_at.desc()).all()
    return users


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Создать нового пользователя"""
    # Проверяем, что email не занят
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    
    # Определяем роль
    role = UserRole.ADMIN if user_data.role == "admin" else UserRole.USER
    
    # Создаём пользователя
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Если указана подписка
    if user_data.subscription_plan and user_data.subscription_plan != "none":
        try:
            plan = SubscriptionPlan(user_data.subscription_plan)
        except ValueError:
            plan = SubscriptionPlan.PREMIUM  # По умолчанию premium
        
        subscription = Subscription(
            user_id=user.id,
            plan=plan,
            status=SubscriptionStatus.ACTIVE,
            expires_at=user_data.subscription_expires_at
        )
        db.add(subscription)
        db.commit()
        db.refresh(user)
    
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Обновить пользователя (роль и/или подписку)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Обновляем роль
    if user_data.role is not None:
        user.role = UserRole.ADMIN if user_data.role == "admin" else UserRole.USER
    
    # Обновляем подписку
    if user_data.subscription_plan is not None:
        # Ищем активную подписку
        active_sub = db.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.status == SubscriptionStatus.ACTIVE
        ).first()
        
        if user_data.subscription_plan == "none":
            # Отменяем подписку
            if active_sub:
                active_sub.status = SubscriptionStatus.CANCELLED
        else:
            # Создаём или обновляем подписку
            try:
                plan = SubscriptionPlan(user_data.subscription_plan)
            except ValueError:
                plan = SubscriptionPlan.DEVELOPER
            
            if active_sub:
                active_sub.plan = plan
                active_sub.expires_at = user_data.subscription_expires_at
            else:
                new_sub = Subscription(
                    user_id=user.id,
                    plan=plan,
                    status=SubscriptionStatus.ACTIVE,
                    expires_at=user_data.subscription_expires_at
                )
                db.add(new_sub)
    
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    """Удалить пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Нельзя удалить себя
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Нельзя удалить свой аккаунт")
    
    db.delete(user)
    db.commit()
