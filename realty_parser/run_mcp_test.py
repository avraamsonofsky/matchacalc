"""
Скрипт для тестирования MCP парсера
Использует MCP browser инструменты для парсинга
"""
import json
import re
from typing import Dict, Optional


def extract_data_from_snapshot(snapshot_text: str) -> Dict[str, Optional[str]]:
    """
    Извлечение данных из snapshot текста
    
    Args:
        snapshot_text: Текст snapshot страницы
        
    Returns:
        Словарь с данными
    """
    result = {
        'price': None,
        'area': None,
        'district': None,
        'year': None
    }
    
    # Поиск цены
    price_patterns = [
        r'(\d[\d\s]{4,})\s*₽',
        r'цена[:\s]+(\d[\d\s]{4,})',
        r'стоимость[:\s]+(\d[\d\s]{4,})',
        r'(\d[\d\s]{4,})\s*руб',
    ]
    
    for pattern in price_patterns:
        matches = re.finditer(pattern, snapshot_text, re.I)
        for match in matches:
            price = match.group(1).replace(' ', '').replace('\xa0', '')
            if price and len(price) > 4:
                result['price'] = price
                break
        if result['price']:
            break
    
    # Поиск площади
    area_patterns = [
        r'(\d+(?:[.,]\d+)?)\s*м²',
        r'площадь[:\s]+(\d+(?:[.,]\d+)?)',
    ]
    
    for pattern in area_patterns:
        match = re.search(pattern, snapshot_text, re.I)
        if match:
            area = match.group(1).replace(',', '.')
            result['area'] = str(int(float(area)))
            break
    
    # Поиск района
    moscow_districts = {
        'москва-сити': 'Москва-Сити',
        'большой сити': 'Большой Сити',
        'центр внутри ттк': 'Центр внутри ТТК',
        'внутри мкад вне ттк': 'Внутри МКАД вне ТТК',
        'за мкад': 'За МКАД',
        'люберцы': 'За МКАД',  # Люберцы находится за МКАД
    }
    
    snapshot_lower = snapshot_text.lower()
    for district_key, district_value in moscow_districts.items():
        if district_key in snapshot_lower:
            result['district'] = district_value
            break
    
    # Поиск года
    year_patterns = [
        r'(\d{4})\s*год',
        r'построен[ая]?\s*в\s*(\d{4})',
        r'год\s*постройки[:\s]+(\d{4})',
        r'ввод\s*в\s*эксплуатацию[:\s]+(\d{4})',
    ]
    
    for pattern in year_patterns:
        match = re.search(pattern, snapshot_text, re.I)
        if match:
            year = match.group(1)
            if 1900 <= int(year) <= 2030:
                result['year'] = year
                break
    
    return result


def parse_with_mcp(url: str) -> Dict[str, Optional[str]]:
    """
    Парсинг URL через MCP инструменты
    Эта функция должна вызываться в контексте с доступом к MCP инструментам
    """
    # В реальном использовании здесь будут вызовы MCP инструментов:
    # mcp_cursor-ide-browser_browser_navigate(url=url)
    # snapshot = mcp_cursor-ide-browser_browser_snapshot()
    # Затем извлечение данных из snapshot
    
    # Для демонстрации возвращаем пустой результат
    # В реальной реализации здесь будет код с использованием MCP инструментов
    return {
        'price': None,
        'area': None,
        'district': None,
        'year': None
    }


if __name__ == '__main__':
    print("MCP Parser Test")
    print("="*60)
    print("Этот скрипт должен вызываться с доступом к MCP инструментам")
    print("Используйте функции напрямую в контексте с MCP")
