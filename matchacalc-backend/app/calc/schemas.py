from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Optional
from app.db.models import PropertyClass


class CalculationRequest(BaseModel):
    purchase_price: float = Field(..., gt=0, description="Стоимость объекта в рублях")
    area: float = Field(..., gt=0, description="Площадь в м²")
    location_group_id: str = Field(..., description="ID группы локаций")
    rve_date: Optional[datetime] = Field(None, description="Дата ввода в эксплуатацию (необязательно, если уже введён)")
    holding_years: int = Field(..., ge=1, le=15, description="Срок владения в годах")
    scenario_id: str = Field(..., description="ID сценария (pes, base, opt)")
    report_id: int = Field(..., description="ID отчёта")
    property_class: Optional[PropertyClass] = Field(PropertyClass.A, description="Класс недвижимости")
    wacc: Optional[float] = Field(None, ge=0, le=100, description="WACC компании-покупателя в процентах (например, 12). Если не указан — NPV не рассчитывается.")


class StaticMetrics(BaseModel):
    payback_rent_years: float
    payback_rent_sale_years: float
    double_price_years: float


class DynamicMetrics(BaseModel):
    holding_years: int
    rent_income_total: float
    rent_income_yield_percent: float
    sale_profit: float
    sale_profit_percent: float
    total_profit: float
    total_profit_percent: float
    npv: Optional[float] = None  # Рублей. None, если WACC не указан
    irr_percent: float


class CashFlow(BaseModel):
    year: int
    cf: float


class CalculationResponse(BaseModel):
    static_metrics: StaticMetrics
    dynamic_metrics: DynamicMetrics
    cash_flows: List[CashFlow]
