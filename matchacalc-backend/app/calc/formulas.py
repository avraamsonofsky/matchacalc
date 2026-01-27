"""
Математические формулы для расчёта доходности недвижимости
Согласно ТЗ, раздел 4
"""
import math
from typing import List, Dict


def calculate_rent_income(
    area: float,
    rent_start: float,  # R0 в руб/м²/год (годовая ставка)
    rent_growth_annual: float,  # g_r'
    holding_years: int
) -> float:
    """
    Расчёт совокупной прибыли от аренды за N лет
    
    Год 1: Rent_1 = 0.5 * A * R0 (6 месяцев подготовки)
    Год t >= 2: Rent_t = A * R0 * (1 + g_r')^(t-2)
    """
    total_income = 0.0
    
    # Год 1: 6 месяцев аренды (половина годовой ставки)
    rent_year_1 = 0.5 * area * rent_start
    total_income += rent_year_1
    
    # Годы 2..N
    for year in range(2, holding_years + 1):
        rent_year = area * rent_start * ((1 + rent_growth_annual) ** (year - 2))
        total_income += rent_year
    
    return total_income


def calculate_sale_price(
    purchase_price: float,
    price_growth_annual: float,  # g_p'
    holding_years: int
) -> float:
    """
    Расчёт стоимости объекта к концу года t
    Price_t = P0 * (1 + g_p')^t
    """
    return purchase_price * ((1 + price_growth_annual) ** holding_years)


def calculate_sale_profit(
    purchase_price: float,
    price_growth_annual: float,
    holding_years: int
) -> float:
    """Прибыль от продажи"""
    sale_price = calculate_sale_price(purchase_price, price_growth_annual, holding_years)
    return sale_price - purchase_price


def calculate_payback_rent(
    purchase_price: float,
    area: float,
    rent_start: float,  # R0 в руб/м²/год (годовая ставка)
    rent_growth_annual: float,
    max_years: int = 50
) -> float:
    """
    Срок окупаемости при сдаче в аренду (без продажи)
    Находим минимальный t, при котором SUM(i=1 to t) Rent_i >= P0
    """
    accumulated = 0.0
    
    # Год 1 (6 месяцев аренды - половина годовой)
    rent_year_1 = 0.5 * area * rent_start
    accumulated += rent_year_1
    if accumulated >= purchase_price:
        return 1.0
    
    # Годы 2..N
    for year in range(2, max_years + 1):
        rent_year = area * rent_start * ((1 + rent_growth_annual) ** (year - 2))
        accumulated += rent_year
        
        if accumulated >= purchase_price:
            # Линейная интерполяция для точности
            if year > 2:
                prev_accumulated = accumulated - rent_year
                remaining = purchase_price - prev_accumulated
                fraction = remaining / rent_year
                return year - 1 + fraction
            else:
                remaining = purchase_price - (accumulated - rent_year)
                fraction = remaining / rent_year
                return 1.0 + fraction
    
    return float(max_years)  # Не окупится за max_years лет


def calculate_payback_rent_and_sale(
    purchase_price: float,
    area: float,
    rent_start: float,  # R0 в руб/м²/год (годовая ставка)
    rent_growth_annual: float,
    price_growth_annual: float,
    max_years: int = 50
) -> float:
    """
    Оптимальный срок владения для удвоения вложенной суммы
    Находим минимальный t, при котором SUM(i=1 to t) Rent_i + Price_t >= 2 * P0
    
    Формула:
    Находим минимальный t: SUM(i=1 to t) Rent_i + Price_t >= 2 * P0
    
    где:
    - Rent_1 = 0.5 * A * R0 (6 месяцев подготовки)
    - Rent_t = A * R0 * (1 + g_r')^(t-2) для t >= 2
    - Price_t = P0 * (1 + g_p')^t
    """
    target_value = 2.0 * purchase_price  # Удвоение вложенной суммы
    accumulated_rent = 0.0
    
    # Год 1 (6 месяцев аренды - половина годовой)
    rent_year_1 = 0.5 * area * rent_start
    accumulated_rent += rent_year_1
    
    # Проверяем год 1
    sale_price_1 = calculate_sale_price(purchase_price, price_growth_annual, 1)
    if accumulated_rent + sale_price_1 >= target_value:
        # Интерполяция для года 1
        if accumulated_rent >= target_value:
            return 1.0
        remaining = target_value - accumulated_rent
        if sale_price_1 > 0:
            # Линейная интерполяция в пределах года
            fraction = remaining / sale_price_1
            return 1.0 + fraction * 0.5  # Упрощённо
        return 1.0
    
    # Годы 2..N
    for year in range(2, max_years + 1):
        rent_year = area * rent_start * ((1 + rent_growth_annual) ** (year - 2))
        accumulated_rent += rent_year
        
        sale_price = calculate_sale_price(purchase_price, price_growth_annual, year)
        total_value = accumulated_rent + sale_price
        
        if total_value >= target_value:
            # Линейная интерполяция между годами
            if year > 2:
                prev_rent = accumulated_rent - rent_year
                prev_sale = calculate_sale_price(purchase_price, price_growth_annual, year - 1)
                prev_total = prev_rent + prev_sale
                remaining = target_value - prev_total
                growth = total_value - prev_total
                if growth > 0:
                    fraction = remaining / growth
                    return year - 1 + fraction
            else:
                # Для года 2
                prev_rent = rent_year_1
                prev_sale = sale_price_1
                prev_total = prev_rent + prev_sale
                remaining = target_value - prev_total
                growth = total_value - prev_total
                if growth > 0:
                    fraction = remaining / growth
                    return 1.0 + fraction
            return float(year)
    
    return float(max_years)


def calculate_double_price(
    price_growth_annual: float
) -> float:
    """
    Срок удвоения стоимости
    T_2x = LN(2) / LN(1 + g_p')
    """
    if price_growth_annual <= 0:
        return float('inf')
    return math.log(2) / math.log(1 + price_growth_annual)


def calculate_npv(
    purchase_price: float,
    area: float,
    rent_start: float,  # R0 в руб/м²/год (годовая ставка)
    rent_growth_annual: float,
    price_growth_annual: float,
    holding_years: int,
    discount_rate: float = 0.12  # Ставка дисконтирования по умолчанию 12%
) -> float:
    """
    NPV (чистая приведённая стоимость)
    NPV = SUM(t=0 to N) CF_t / (1+d)^t
    
    CF_0 = -P0
    CF_t (1..N-1) = Rent_t
    CF_N = Rent_N + Price_N
    """
    npv = -purchase_price  # CF_0
    
    # Год 1 (6 месяцев аренды)
    rent_year_1 = 0.5 * area * rent_start
    npv += rent_year_1 / ((1 + discount_rate) ** 1)
    
    # Годы 2..N-1
    for year in range(2, holding_years):
        rent_year = area * rent_start * ((1 + rent_growth_annual) ** (year - 2))
        npv += rent_year / ((1 + discount_rate) ** year)
    
    # Год N (последний)
    if holding_years >= 2:
        rent_year_n = area * rent_start * ((1 + rent_growth_annual) ** (holding_years - 2))
        sale_price = calculate_sale_price(purchase_price, price_growth_annual, holding_years)
        cf_n = rent_year_n + sale_price
        npv += cf_n / ((1 + discount_rate) ** holding_years)
    
    return npv


def calculate_irr(
    purchase_price: float,
    area: float,
    rent_start: float,
    rent_growth_annual: float,
    price_growth_annual: float,
    holding_years: int,
    precision: float = 0.0001  # 0.01%
) -> float:
    """
    IRR (внутренняя норма доходности)
    IRR — ставка r, при которой NPV(r) = 0
    Вычисляется методом двоичного поиска
    """
    def npv_at_rate(rate: float) -> float:
        return calculate_npv(
            purchase_price, area, rent_start, rent_growth_annual,
            price_growth_annual, holding_years, rate
        )
    
    # Проверяем, что при rate=0 NPV положительна (прибыль есть)
    npv_at_zero = npv_at_rate(0.0001)  # Маленькая ставка вместо 0 для избежания деления
    if npv_at_zero <= 0:
        return 0.0  # Проект убыточен, IRR не существует
    
    # Начальные границы поиска
    low = 0.0
    high = 1.0  # 100%
    
    # Расширяем верхнюю границу, пока NPV не станет отрицательной
    while npv_at_rate(high) > 0:
        high *= 2
        if high > 10:  # Защита от бесконечного цикла (IRR > 1000%)
            return high  # Очень высокая доходность
    
    # Двоичный поиск IRR
    # При низкой ставке NPV > 0, при высокой NPV < 0
    while high - low > precision:
        mid = (low + high) / 2
        npv_mid = npv_at_rate(mid)
        
        if abs(npv_mid) < precision:
            return mid
        
        if npv_mid > 0:
            low = mid  # IRR выше, чем mid
        else:
            high = mid  # IRR ниже, чем mid
    
    return (low + high) / 2


def calculate_cash_flows(
    purchase_price: float,
    area: float,
    rent_start: float,  # R0 в руб/м²/год (годовая ставка)
    rent_growth_annual: float,
    price_growth_annual: float,
    holding_years: int
) -> List[Dict[str, float]]:
    """
    Генерация денежных потоков для всех лет
    Возвращает список: [{"year": 0, "cf": -P0}, {"year": 1, "cf": Rent_1}, ...]
    """
    cash_flows = [{"year": 0, "cf": -purchase_price}]
    
    # Год 1 (6 месяцев аренды)
    rent_year_1 = 0.5 * area * rent_start
    cash_flows.append({"year": 1, "cf": rent_year_1})
    
    # Годы 2..N-1
    for year in range(2, holding_years):
        rent_year = area * rent_start * ((1 + rent_growth_annual) ** (year - 2))
        cash_flows.append({"year": year, "cf": rent_year})
    
    # Год N (последний)
    if holding_years >= 2:
        rent_year_n = area * rent_start * ((1 + rent_growth_annual) ** (holding_years - 2))
        sale_price = calculate_sale_price(purchase_price, price_growth_annual, holding_years)
        cf_n = rent_year_n + sale_price
        cash_flows.append({"year": holding_years, "cf": cf_n})
    
    return cash_flows
