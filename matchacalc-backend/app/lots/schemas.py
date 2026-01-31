"""Схемы для лотов"""
from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


class LotBase(BaseModel):
    purchase_price: float
    area: float
    address: str
    location_group_id: str
    rve_date: datetime
    layout_image_url: Optional[str] = None
    custom_discount_percent: Optional[float] = None


class LotCreate(LotBase):
    cian_url: Optional[str] = None


class LotFromUrl(BaseModel):
    """Создание лота из URL Циан"""
    url: str
    collection_id: Optional[int] = None


class LotResponse(LotBase):
    id: int
    owner_user_id: Optional[int]
    cian_url: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class LotPublicResponse(BaseModel):
    """Публичный ответ о лоте (для подборок)"""
    id: int
    layout_image_url: Optional[str]
    address: str
    original_price: float
    discounted_price: Optional[float]
    discount_percent: Optional[float]
    area: float
    location_group_id: str
    rve_date: datetime
    
    class Config:
        from_attributes = True


class ParsedLotData(BaseModel):
    """Данные, извлечённые из URL"""
    price: Optional[str] = None
    area: Optional[str] = None
    district: Optional[str] = None
    year: Optional[str] = None
    address: Optional[str] = None
