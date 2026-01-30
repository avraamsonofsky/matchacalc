from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.db.database import Base


# Enums
class UserRole(str, enum.Enum):
    USER = "user"
    AGENT = "agent"
    DEVELOPER = "developer"
    ADMIN = "admin"


class SubscriptionPlan(str, enum.Enum):
    NONE = "none"
    AGENT = "agent"
    DEVELOPER = "developer"
    PREMIUM = "premium"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class PropertyClass(str, enum.Enum):
    A_PRIME = "A_Prime"
    A = "A"
    B_PLUS = "B_plus"
    B = "B"


# Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    collections = relationship("Collection", back_populates="owner", cascade="all, delete-orphan")
    calculations = relationship("Calculation", back_populates="user")


class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan = Column(SQLEnum(SubscriptionPlan), default=SubscriptionPlan.NONE, nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")


class LocationGroup(Base):
    __tablename__ = "location_groups"
    
    id = Column(String, primary_key=True, index=True)  # например "moscow_city"
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    report_mapping = Column(JSON, nullable=True)  # список субрынков/районов
    
    # Relationships
    market_report_values = relationship("MarketReportValue", back_populates="location_group")
    lots = relationship("Lot", back_populates="location_group")


class MarketReport(Base):
    __tablename__ = "market_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, nullable=False)  # nikoliers, nf_group, etc.
    title = Column(String, nullable=False)
    period = Column(String, nullable=False)  # например "2025-Q3"
    file_url = Column(String, nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    values = relationship("MarketReportValue", back_populates="report", cascade="all, delete-orphan")


class MarketReportValue(Base):
    __tablename__ = "market_report_values"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("market_reports.id"), nullable=False)
    location_group_id = Column(String, ForeignKey("location_groups.id"), nullable=False)
    property_class = Column(SQLEnum(PropertyClass), nullable=False)
    rent_start = Column(Float, nullable=False)  # R0 в руб/м²/мес
    rent_growth_annual = Column(Float, nullable=False)  # g_r
    price_per_m2_start = Column(Float, nullable=True)  # V0
    price_growth_annual = Column(Float, nullable=False)  # g_p
    vacancy_rate = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    report = relationship("MarketReport", back_populates="values")
    location_group = relationship("LocationGroup", back_populates="market_report_values")


class ScenarioConfig(Base):
    __tablename__ = "scenario_configs"
    
    id = Column(String, primary_key=True)  # pes, base, opt
    name = Column(String, nullable=False)  # Пессимистичный, Базовый, Оптимистичный
    rent_growth_multiplier = Column(Float, nullable=False)  # k_s для аренды
    price_growth_multiplier = Column(Float, nullable=False)  # k_s для цены
    discount_rate_adjustment = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Lot(Base):
    __tablename__ = "lots"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    cian_url = Column(String, nullable=False, unique=True)
    purchase_price = Column(Float, nullable=False)
    area = Column(Float, nullable=False)
    address = Column(String, nullable=False)
    location_group_id = Column(String, ForeignKey("location_groups.id"), nullable=False)
    rve_date = Column(DateTime(timezone=True), nullable=False)
    layout_image_url = Column(String, nullable=True)
    custom_discount_percent = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    location_group = relationship("LocationGroup", back_populates="lots")
    collection_lots = relationship("CollectionLot", back_populates="lot", cascade="all, delete-orphan")


class Collection(Base):
    __tablename__ = "collections"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    public_slug = Column(String, unique=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="collections")
    collection_lots = relationship("CollectionLot", back_populates="collection", cascade="all, delete-orphan")


class CollectionLot(Base):
    __tablename__ = "collection_lots"
    
    collection_id = Column(Integer, ForeignKey("collections.id"), primary_key=True)
    lot_id = Column(Integer, ForeignKey("lots.id"), primary_key=True)
    position = Column(Integer, default=0, nullable=False)
    
    # Relationships
    collection = relationship("Collection", back_populates="collection_lots")
    lot = relationship("Lot", back_populates="collection_lots")


class Calculation(Base):
    __tablename__ = "calculations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    lot_id = Column(Integer, ForeignKey("lots.id"), nullable=True)
    purchase_price = Column(Float, nullable=False)
    area = Column(Float, nullable=False)
    location_group_id = Column(String, nullable=False)
    rve_date = Column(DateTime(timezone=True), nullable=False)
    holding_years = Column(Integer, nullable=False)
    scenario_id = Column(String, nullable=False)
    report_id = Column(Integer, nullable=False)
    result_json = Column(JSON, nullable=False)  # все рассчитанные метрики и cash-flows
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="calculations")
