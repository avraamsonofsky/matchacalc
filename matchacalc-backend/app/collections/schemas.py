"""Схемы для коллекций"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.lots.schemas import LotPublicResponse


class CollectionBase(BaseModel):
    name: str
    description: Optional[str] = None


class CollectionCreate(CollectionBase):
    pass


class CollectionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class CollectionResponse(CollectionBase):
    id: int
    owner_user_id: int
    public_slug: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    lots_count: int = 0
    
    class Config:
        from_attributes = True


class CollectionDetailResponse(CollectionResponse):
    """Детальный ответ с лотами"""
    lots: List[LotPublicResponse] = []


class CollectionPublicResponse(BaseModel):
    """Публичный просмотр коллекции"""
    title: str
    description: Optional[str]
    lots: List[LotPublicResponse]


class AddLotsRequest(BaseModel):
    """Запрос на добавление лотов из URL"""
    cian_urls: List[str]


class PublishResponse(BaseModel):
    """Ответ на публикацию коллекции"""
    public_slug: str
    public_url: str
