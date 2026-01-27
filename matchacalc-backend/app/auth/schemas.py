from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.db.models import SubscriptionPlan, SubscriptionStatus


class UserRegister(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SubscriptionInfo(BaseModel):
    plan: SubscriptionPlan
    status: SubscriptionStatus
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    subscription: Optional[SubscriptionInfo] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
