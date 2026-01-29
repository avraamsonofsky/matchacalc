from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.db.models import PropertyClass


class MarketReportValueInJson(BaseModel):
    """Значение отчёта в JSON-загрузке"""
    location_group_id: str
    property_class: str  # "A_Prime", "A", "B_plus", "B"
    rent_start: float
    rent_growth_annual: float
    price_per_m2_start: Optional[float] = None
    price_growth_annual: float
    vacancy_rate: Optional[float] = None


class MarketReportInJson(BaseModel):
    """Отчёт в JSON-загрузке"""
    provider: str
    title: str
    period: str
    file_url: Optional[str] = None
    active: bool = True
    values: List[MarketReportValueInJson] = []


class MarketReportCreate(BaseModel):
    provider: str
    title: str
    period: str
    file_url: Optional[str] = None
    active: bool = True


class MarketReportValueCreate(BaseModel):
    report_id: int
    location_group_id: str
    property_class: PropertyClass
    rent_start: float  # руб/м²/мес
    rent_growth_annual: float
    price_per_m2_start: Optional[float] = None
    price_growth_annual: float
    vacancy_rate: Optional[float] = None


class MarketReportUpdate(BaseModel):
    provider: Optional[str] = None
    title: Optional[str] = None
    period: Optional[str] = None
    file_url: Optional[str] = None
    active: Optional[bool] = None


class MarketReportValueUpdate(BaseModel):
    rent_start: Optional[float] = None
    rent_growth_annual: Optional[float] = None
    price_per_m2_start: Optional[float] = None
    price_growth_annual: Optional[float] = None
    vacancy_rate: Optional[float] = None


class LocationGroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    report_mapping: Optional[dict] = None


class ScenarioConfigUpdate(BaseModel):
    name: Optional[str] = None
    rent_growth_multiplier: Optional[float] = None
    price_growth_multiplier: Optional[float] = None
    discount_rate_adjustment: Optional[float] = None


class LocationGroupCreate(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    report_mapping: Optional[dict] = None


class ScenarioConfigCreate(BaseModel):
    id: str
    name: str
    rent_growth_multiplier: float
    price_growth_multiplier: float
    discount_rate_adjustment: Optional[float] = None


class MarketReportResponse(BaseModel):
    id: int
    provider: str
    title: str
    period: str
    file_url: Optional[str]
    active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class MarketReportValueResponse(BaseModel):
    id: int
    report_id: int
    location_group_id: str
    property_class: PropertyClass
    rent_start: float
    rent_growth_annual: float
    price_per_m2_start: Optional[float]
    price_growth_annual: float
    vacancy_rate: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True
