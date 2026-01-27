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
