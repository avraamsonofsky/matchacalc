"""API маршруты для коллекций"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
import secrets
import string

from app.db.database import get_db
from app.db.models import Collection, CollectionLot, Lot, User, SubscriptionStatus
from app.collections.schemas import (
    CollectionCreate, CollectionUpdate, CollectionResponse,
    CollectionDetailResponse, CollectionPublicResponse,
    AddLotsRequest, PublishResponse
)
from app.lots.schemas import LotPublicResponse
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


def generate_slug(length: int = 8) -> str:
    """Генерация уникального slug"""
    chars = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


@router.get("", response_model=List[CollectionResponse])
def get_collections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список коллекций текущего пользователя"""
    collections = db.query(Collection).filter(
        Collection.owner_user_id == current_user.id
    ).order_by(Collection.created_at.desc()).all()
    
    # Добавляем количество лотов
    result = []
    for coll in collections:
        lots_count = db.query(CollectionLot).filter(
            CollectionLot.collection_id == coll.id
        ).count()
        
        resp = CollectionResponse(
            id=coll.id,
            owner_user_id=coll.owner_user_id,
            name=coll.name,
            description=coll.description,
            public_slug=coll.public_slug,
            created_at=coll.created_at,
            updated_at=coll.updated_at,
            lots_count=lots_count
        )
        result.append(resp)
    
    return result


@router.post("", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
def create_collection(
    data: CollectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_subscription)
):
    """Создать новую коллекцию (только для подписчиков)"""
    collection = Collection(
        owner_user_id=current_user.id,
        name=data.name,
        description=data.description
    )
    
    db.add(collection)
    db.commit()
    db.refresh(collection)
    
    return CollectionResponse(
        id=collection.id,
        owner_user_id=collection.owner_user_id,
        name=collection.name,
        description=collection.description,
        public_slug=collection.public_slug,
        created_at=collection.created_at,
        updated_at=collection.updated_at,
        lots_count=0
    )


@router.get("/{collection_id}", response_model=CollectionDetailResponse)
def get_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить коллекцию с лотами (для владельца)"""
    collection = db.query(Collection).filter(
        Collection.id == collection_id,
        Collection.owner_user_id == current_user.id
    ).first()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Коллекция не найдена")
    
    # Получаем лоты
    collection_lots = db.query(CollectionLot).filter(
        CollectionLot.collection_id == collection_id
    ).order_by(CollectionLot.position).all()
    
    lots = []
    for cl in collection_lots:
        lot = db.query(Lot).filter(Lot.id == cl.lot_id).first()
        if lot:
            discounted_price = None
            if lot.custom_discount_percent:
                discounted_price = lot.purchase_price * (1 - lot.custom_discount_percent / 100)
            
            lots.append(LotPublicResponse(
                id=lot.id,
                layout_image_url=lot.layout_image_url,
                address=lot.address,
                original_price=lot.purchase_price,
                discounted_price=discounted_price,
                discount_percent=lot.custom_discount_percent,
                area=lot.area,
                location_group_id=lot.location_group_id,
                rve_date=lot.rve_date
            ))
    
    return CollectionDetailResponse(
        id=collection.id,
        owner_user_id=collection.owner_user_id,
        name=collection.name,
        description=collection.description,
        public_slug=collection.public_slug,
        created_at=collection.created_at,
        updated_at=collection.updated_at,
        lots_count=len(lots),
        lots=lots
    )


@router.put("/{collection_id}", response_model=CollectionResponse)
def update_collection(
    collection_id: int,
    data: CollectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить коллекцию"""
    collection = db.query(Collection).filter(
        Collection.id == collection_id,
        Collection.owner_user_id == current_user.id
    ).first()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Коллекция не найдена")
    
    if data.name is not None:
        collection.name = data.name
    if data.description is not None:
        collection.description = data.description
    
    db.commit()
    db.refresh(collection)
    
    lots_count = db.query(CollectionLot).filter(
        CollectionLot.collection_id == collection.id
    ).count()
    
    return CollectionResponse(
        id=collection.id,
        owner_user_id=collection.owner_user_id,
        name=collection.name,
        description=collection.description,
        public_slug=collection.public_slug,
        created_at=collection.created_at,
        updated_at=collection.updated_at,
        lots_count=lots_count
    )


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить коллекцию"""
    collection = db.query(Collection).filter(
        Collection.id == collection_id,
        Collection.owner_user_id == current_user.id
    ).first()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Коллекция не найдена")
    
    db.delete(collection)
    db.commit()


@router.post("/{collection_id}/lots")
async def add_lots_to_collection(
    collection_id: int,
    data: AddLotsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_subscription)
):
    """Добавить лоты в коллекцию через URL"""
    collection = db.query(Collection).filter(
        Collection.id == collection_id,
        Collection.owner_user_id == current_user.id
    ).first()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Коллекция не найдена")
    
    # Проверяем текущее количество лотов
    current_count = db.query(CollectionLot).filter(
        CollectionLot.collection_id == collection_id
    ).count()
    
    if current_count + len(data.cian_urls) > 20:
        raise HTTPException(
            status_code=400,
            detail=f"Превышен лимит лотов. Текущее: {current_count}, максимум: 20"
        )
    
    # Импортируем функцию из lots
    from app.lots.routes import import_from_cian
    from app.lots.schemas import LotFromUrl
    
    added = []
    errors = []
    
    for url in data.cian_urls:
        try:
            lot_data = LotFromUrl(url=url, collection_id=collection_id)
            lot = await import_from_cian(lot_data, db, current_user)
            added.append({"url": url, "lot_id": lot.id})
        except Exception as e:
            errors.append({"url": url, "error": str(e)})
    
    return {
        "added": added,
        "errors": errors,
        "total_added": len(added)
    }


@router.delete("/{collection_id}/lots/{lot_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_lot_from_collection(
    collection_id: int,
    lot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить лот из коллекции"""
    collection = db.query(Collection).filter(
        Collection.id == collection_id,
        Collection.owner_user_id == current_user.id
    ).first()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Коллекция не найдена")
    
    collection_lot = db.query(CollectionLot).filter(
        CollectionLot.collection_id == collection_id,
        CollectionLot.lot_id == lot_id
    ).first()
    
    if collection_lot:
        db.delete(collection_lot)
        db.commit()


@router.post("/{collection_id}/publish", response_model=PublishResponse)
def publish_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_subscription)
):
    """Опубликовать коллекцию (генерация публичной ссылки)"""
    collection = db.query(Collection).filter(
        Collection.id == collection_id,
        Collection.owner_user_id == current_user.id
    ).first()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Коллекция не найдена")
    
    # Генерируем slug если его нет
    if not collection.public_slug:
        while True:
            slug = generate_slug()
            existing = db.query(Collection).filter(
                Collection.public_slug == slug
            ).first()
            if not existing:
                break
        
        collection.public_slug = slug
        db.commit()
        db.refresh(collection)
    
    return PublishResponse(
        public_slug=collection.public_slug,
        public_url=f"/c/{collection.public_slug}"
    )


@router.get("/public/{slug}", response_model=CollectionPublicResponse)
def get_public_collection(
    slug: str,
    db: Session = Depends(get_db)
):
    """Публичный просмотр коллекции по slug (без авторизации)"""
    collection = db.query(Collection).filter(
        Collection.public_slug == slug
    ).first()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Коллекция не найдена")
    
    # Получаем лоты
    collection_lots = db.query(CollectionLot).filter(
        CollectionLot.collection_id == collection.id
    ).order_by(CollectionLot.position).all()
    
    lots = []
    for cl in collection_lots:
        lot = db.query(Lot).filter(Lot.id == cl.lot_id).first()
        if lot:
            discounted_price = None
            if lot.custom_discount_percent:
                discounted_price = lot.purchase_price * (1 - lot.custom_discount_percent / 100)
            
            lots.append(LotPublicResponse(
                id=lot.id,
                layout_image_url=lot.layout_image_url,
                address=lot.address,
                original_price=lot.purchase_price,
                discounted_price=discounted_price,
                discount_percent=lot.custom_discount_percent,
                area=lot.area,
                location_group_id=lot.location_group_id,
                rve_date=lot.rve_date
            ))
    
    return CollectionPublicResponse(
        title=collection.name,
        description=collection.description,
        lots=lots
    )
