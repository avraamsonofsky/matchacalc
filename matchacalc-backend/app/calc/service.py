from sqlalchemy.orm import Session
from app.db.models import MarketReportValue, ScenarioConfig, LocationGroup, PropertyClass
from app.calc.formulas import (
    calculate_rent_income, calculate_sale_profit, calculate_payback_rent,
    calculate_payback_rent_and_sale, calculate_double_price,
    calculate_npv, calculate_irr, calculate_cash_flows
)
from typing import Optional


def get_market_data(
    db: Session,
    report_id: int,
    location_group_id: str,
    property_class: PropertyClass = PropertyClass.A
) -> Optional[MarketReportValue]:
    """Получение данных рынка для расчёта"""
    return db.query(MarketReportValue).filter(
        MarketReportValue.report_id == report_id,
        MarketReportValue.location_group_id == location_group_id,
        MarketReportValue.property_class == property_class
    ).first()


def get_scenario_config(db: Session, scenario_id: str) -> Optional[ScenarioConfig]:
    """Получение конфигурации сценария"""
    return db.query(ScenarioConfig).filter(ScenarioConfig.id == scenario_id).first()


def calculate_metrics(
    db: Session,
    purchase_price: float,
    area: float,
    location_group_id: str,
    report_id: int,
    scenario_id: str,
    holding_years: int,
    property_class: PropertyClass = PropertyClass.A,
    discount_rate: Optional[float] = None  # None => NPV не считается
) -> dict:
    """
    Основная функция расчёта всех метрик
    """
    # Получаем данные рынка
    market_data = get_market_data(db, report_id, location_group_id, property_class)
    if not market_data:
        raise ValueError(f"Данные рынка не найдены для report_id={report_id}, location_group_id={location_group_id}, property_class={property_class}")
    
    # Получаем конфигурацию сценария
    scenario = get_scenario_config(db, scenario_id)
    if not scenario:
        raise ValueError(f"Сценарий не найден: {scenario_id}")
    
    # Применяем коэффициенты сценария
    rent_growth_effective = market_data.rent_growth_annual * scenario.rent_growth_multiplier
    price_growth_effective = market_data.price_growth_annual * scenario.price_growth_multiplier
    
    # rent_start уже в годовом выражении (руб/м²/год)
    
    # Статические метрики
    payback_rent_years = calculate_payback_rent(
        purchase_price, area, market_data.rent_start, rent_growth_effective
    )
    
    payback_rent_sale_years = calculate_payback_rent_and_sale(
        purchase_price, area, market_data.rent_start,
        rent_growth_effective, price_growth_effective
    )
    
    double_price_years = calculate_double_price(price_growth_effective)
    
    # Динамические метрики
    rent_income_total = calculate_rent_income(
        area, market_data.rent_start, rent_growth_effective, holding_years
    )
    
    sale_profit = calculate_sale_profit(
        purchase_price, price_growth_effective, holding_years
    )
    
    total_profit = rent_income_total + sale_profit
    
    # Проценты (за весь срок владения, не среднегодовые)
    rent_yield_percent = rent_income_total / purchase_price if purchase_price > 0 else 0
    sale_profit_percent = sale_profit / purchase_price if purchase_price > 0 else 0
    total_profit_percent = total_profit / purchase_price if purchase_price > 0 else 0
    
    # NPV: только если discount_rate (WACC) указан
    if discount_rate is not None:
        npv = calculate_npv(
            purchase_price, area, market_data.rent_start,
            rent_growth_effective, price_growth_effective,
            holding_years, discount_rate
        )
    else:
        npv = None
    
    irr = calculate_irr(
        purchase_price, area, market_data.rent_start,
        rent_growth_effective, price_growth_effective, holding_years
    )
    
    # Cash flows
    cash_flows = calculate_cash_flows(
        purchase_price, area, market_data.rent_start,
        rent_growth_effective, price_growth_effective, holding_years
    )
    
    return {
        "static_metrics": {
            "payback_rent_years": payback_rent_years,
            "payback_rent_sale_years": payback_rent_sale_years,
            "double_price_years": double_price_years
        },
        "dynamic_metrics": {
            "holding_years": holding_years,
            "rent_income_total": rent_income_total,
            "rent_income_yield_percent": rent_yield_percent,
            "sale_profit": sale_profit,
            "sale_profit_percent": sale_profit_percent,
            "total_profit": total_profit,
            "total_profit_percent": total_profit_percent,
            "npv": npv,
            "irr_percent": irr
        },
        "cash_flows": cash_flows
    }
