from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://matchacalc:secret@localhost:5432/matchacalc"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 129600  # 3 месяца (90 дней * 24 часа * 60 минут)
    
    # Rate Limiting (в секундах)
    RATE_LIMIT_GUEST: int = 180  # 3 минуты
    RATE_LIMIT_USER: int = 60    # 1 минута
    RATE_LIMIT_SUBSCRIBER: int = 10  # 10 секунд
    
    # Billing
    AGENT_SUBSCRIPTION_PRICE: float = 2999.0
    STRIPE_KEY: Optional[str] = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
