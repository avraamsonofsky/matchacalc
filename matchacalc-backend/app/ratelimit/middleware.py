from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import redis
import time
from app.config import settings
from app.db.database import get_db
from app.auth.dependencies import get_current_user
from app.db.models import SubscriptionStatus
from typing import Optional


redis_client = None


def get_redis_client():
    """Получение клиента Redis"""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return redis_client


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware для ограничения частоты запросов"""
    
    async def dispatch(self, request: Request, call_next):
        # Применяем rate-limiting только к эндпоинтам калькулятора
        if not request.url.path.startswith("/api/v1/calc"):
            response = await call_next(request)
            return response
        
        # Определяем ключ для rate-limiting
        user_id = None
        subscription_status = None
        
        # Пытаемся получить пользователя из токена
        try:
            # Простая проверка токена без полной аутентификации
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                from app.auth.jwt_handler import decode_access_token
                payload = decode_access_token(token)
                if payload:
                    user_id = payload.get("sub")
                    # Получаем статус подписки из БД
                    from app.db.database import SessionLocal
                    db = SessionLocal()
                    try:
                        from app.db.models import User, Subscription
                        user = db.query(User).filter(User.id == user_id).first()
                        if user:
                            subscription = db.query(Subscription).filter(
                                Subscription.user_id == user_id,
                                Subscription.status == SubscriptionStatus.ACTIVE
                            ).first()
                            if subscription:
                                subscription_status = subscription.plan.value
                    finally:
                        db.close()
        except Exception:
            pass
        
        # Определяем лимит
        if subscription_status == "AGENT" or subscription_status == "DEVELOPER":
            limit_seconds = settings.RATE_LIMIT_SUBSCRIBER
            key_prefix = f"ratelimit:subscriber:{user_id}"
        elif user_id:
            limit_seconds = settings.RATE_LIMIT_USER
            key_prefix = f"ratelimit:user:{user_id}"
        else:
            # Гость - используем IP
            client_ip = request.client.host if request.client else "unknown"
            limit_seconds = settings.RATE_LIMIT_GUEST
            key_prefix = f"ratelimit:guest:{client_ip}"
        
        # Проверяем rate limit
        redis_cli = get_redis_client()
        key = f"{key_prefix}:{int(time.time() / limit_seconds)}"
        
        try:
            current = redis_cli.incr(key)
            if current == 1:
                redis_cli.expire(key, limit_seconds)
            
            if current > 1:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Превышен лимит запросов. Попробуйте через {limit_seconds} секунд."
                )
        except redis.RedisError:
            # Если Redis недоступен, пропускаем запрос (fallback)
            pass
        
        response = await call_next(request)
        return response
