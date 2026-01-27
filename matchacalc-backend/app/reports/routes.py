from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import MarketReport, LocationGroup, ScenarioConfig
from app.reports.schemas import MarketReportResponse, LocationGroupResponse, ScenarioResponse

router = APIRouter()


@router.get("/", response_model=List[MarketReportResponse])
def get_reports(db: Session = Depends(get_db)):
    """Список доступных отчётов"""
    reports = db.query(MarketReport).filter(MarketReport.active == True).all()
    return reports


@router.get("/location-groups", response_model=List[LocationGroupResponse])
def get_location_groups(db: Session = Depends(get_db)):
    """Список групп локаций"""
    groups = db.query(LocationGroup).all()
    return groups


@router.get("/scenarios", response_model=List[ScenarioResponse])
def get_scenarios(db: Session = Depends(get_db)):
    """Список сценариев"""
    scenarios = db.query(ScenarioConfig).all()
    return scenarios
