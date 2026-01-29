from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.db.models import PropertyClass


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


class LocationGroupResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    
    class Config:
        from_attributes = True


class ScenarioResponse(BaseModel):
    id: str
    name: str
    rent_growth_multiplier: float
    price_growth_multiplier: float
    discount_rate_adjustment: Optional[float] = None

    class Config:
        from_attributes = True
