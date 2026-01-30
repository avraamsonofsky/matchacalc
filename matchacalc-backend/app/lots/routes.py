"""API маршруты для лотов"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.database import get_db
from app.db.models import Lot, User, Collection, CollectionLot, SubscriptionStatus
from app.lots.schemas import LotResponse, LotFromUrl, LotCreate, ParsedLotData
from app.auth.dependencies import get_current_user, get_optional_user

router = APIRouter()


def require_subscription(current_user: User = Depends(get_current_user)):
    """Проверка наличия активной подписки"""
    has_active_sub = any(
        sub.status == SubscriptionStatus.ACTIVE
        for sub in current_user.subscriptions
    )
    if not has_active_sub:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется активная подписка"
        )
    return current_user


@router.get("/{lot_id}", response_model=LotResponse)
def get_lot(
    lot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """Получить информацию о лоте"""
    lot = db.query(Lot).filter(Lot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Лот не найден")
    return lot


@router.post("/import-from-cian", response_model=LotResponse)
async def import_from_cian(
    data: LotFromUrl,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_subscription)
):
    """
    Импорт лота из URL Циан/Авито/Яндекс.Недвижимость.
    Только для пользователей с подпиской.
    """
    # Проверяем, не существует ли уже этот лот
    existing = db.query(Lot).filter(Lot.cian_url == data.url).first()
    if existing:
        # Если лот существует и нужно добавить в коллекцию
        if data.collection_id:
            add_lot_to_collection(db, data.collection_id, existing.id, current_user.id)
        return existing
    
    # Парсим данные с URL
    parsed = await parse_property_url(data.url)
    
    if not parsed.price or not parsed.area:
        raise HTTPException(
            status_code=400,
            detail="Не удалось получить данные с указанного URL"
        )
    
    # Определяем location_group_id по district
    location_group_id = map_district_to_location_group(parsed.district)
    
    # Создаём лот
    lot = Lot(
        owner_user_id=current_user.id,
        cian_url=data.url,
        purchase_price=float(parsed.price.replace(" ", "")),
        area=float(parsed.area),
        address=parsed.address or "Адрес не определён",
        location_group_id=location_group_id,
        rve_date=datetime.now() if not parsed.year else datetime(int(parsed.year), 1, 1)
    )
    
    db.add(lot)
    db.commit()
    db.refresh(lot)
    
    # Добавляем в коллекцию, если указано
    if data.collection_id:
        add_lot_to_collection(db, data.collection_id, lot.id, current_user.id)
    
    return lot


@router.post("/parse-url", response_model=ParsedLotData)
async def parse_url(
    data: LotFromUrl,
    current_user: User = Depends(require_subscription)
):
    """
    Парсинг URL без сохранения.
    Возвращает извлечённые данные для предпросмотра.
    """
    return await parse_property_url(data.url)


def add_lot_to_collection(db: Session, collection_id: int, lot_id: int, user_id: int):
    """Добавить лот в коллекцию"""
    collection = db.query(Collection).filter(
        Collection.id == collection_id,
        Collection.owner_user_id == user_id
    ).first()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Коллекция не найдена")
    
    # Проверяем лимит в 20 лотов
    lots_count = db.query(CollectionLot).filter(
        CollectionLot.collection_id == collection_id
    ).count()
    
    if lots_count >= 20:
        raise HTTPException(status_code=400, detail="Максимум 20 лотов в коллекции")
    
    # Проверяем, не добавлен ли уже
    existing = db.query(CollectionLot).filter(
        CollectionLot.collection_id == collection_id,
        CollectionLot.lot_id == lot_id
    ).first()
    
    if not existing:
        collection_lot = CollectionLot(
            collection_id=collection_id,
            lot_id=lot_id,
            position=lots_count
        )
        db.add(collection_lot)
        db.commit()


def map_district_to_location_group(district: str | None) -> str:
    """Маппинг района в location_group_id"""
    if not district:
        return "mkad_outside_ttk"  # По умолчанию
    
    district_lower = district.lower()
    
    if "москва-сити" in district_lower or "moscow city" in district_lower:
        return "moscow_city"
    elif "большой сити" in district_lower:
        return "big_city"
    elif "ттк" in district_lower or "центр" in district_lower:
        return "center_ttk"
    elif "мкад" in district_lower and "за" in district_lower:
        return "outside_mkad"
    else:
        return "mkad_outside_ttk"


async def parse_property_url(url: str) -> ParsedLotData:
    """
    Парсинг URL недвижимости.
    Использует универсальный парсер.
    """
    try:
        # Импортируем парсер - проверяем разные пути
        import sys
        import os
        
        parser_paths = [
            '/root/realty_parser',           # Сервер
            '/home/nikit/realty_parser',     # Локальная разработка
            os.path.join(os.path.dirname(__file__), '..', '..', 'realty_parser'),  # Относительный
        ]
        
        parser_path = None
        for path in parser_paths:
            if os.path.exists(path):
                parser_path = path
                break
        
        if not parser_path:
            print(f"Парсер не найден. Проверенные пути: {parser_paths}")
            return ParsedLotData()
        
        sys.path.insert(0, parser_path)
        from universal_parser import parse_url as universal_parse
        
        result = universal_parse(url, method='requests')
        
        return ParsedLotData(
            price=result.get('price'),
            area=result.get('area'),
            district=result.get('district'),
            year=result.get('year'),
            address=result.get('address')
        )
    except Exception as e:
        print(f"Ошибка парсинга: {e}")
        import traceback
        traceback.print_exc()
        return ParsedLotData()
