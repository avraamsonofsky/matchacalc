"""
Парсер через MCP сервер (Model Context Protocol)
Использует браузерные возможности MCP для парсинга
"""
from typing import Dict, Optional
import re


def parse_with_mcp_browser(url: str, mcp_tools) -> Dict[str, Optional[str]]:
    """
    Парсинг с использованием MCP браузерных инструментов
    
    Args:
        url: URL для парсинга
        mcp_tools: Объект с MCP инструментами (browser_navigate, browser_snapshot и т.д.)
    
    Returns:
        Словарь с данными: {'price': str, 'area': str, 'district': str, 'year': str}
    """
    result = {
        'price': None,
        'area': None,
        'district': None,
        'year': None
    }
    
    try:
        # Навигация на страницу
        mcp_tools.browser_navigate(url=url)
        
        # Получение снимка страницы
        snapshot = mcp_tools.browser_snapshot()
        
        # Парсинг данных из snapshot
        # Snapshot содержит структурированные данные о странице
        
        # Поиск цены
        price_patterns = [
            r'(\d[\d\s]*)\s*₽',
            r'цена[:\s]+(\d[\d\s]*)',
            r'стоимость[:\s]+(\d[\d\s]*)',
        ]
        
        snapshot_text = str(snapshot).lower()
        
        for pattern in price_patterns:
            match = re.search(pattern, snapshot_text, re.I)
            if match:
                price = match.group(1).replace(' ', '')
                if price and len(price) > 4:
                    result['price'] = price
                    break
        
        # Поиск площади
        area_match = re.search(r'(\d+(?:[.,]\d+)?)\s*м²', snapshot_text, re.I)
        if area_match:
            area = area_match.group(1).replace(',', '.')
            result['area'] = str(int(float(area)))
        
        # Поиск района
        moscow_districts = [
            'москва-сити', 'большой сити', 'центр внутри ттк',
            'внутри мкад вне ттк', 'за мкад'
        ]
        district_map = {
            'москва-сити': 'Москва-Сити',
            'большой сити': 'Большой Сити',
            'центр внутри ттк': 'Центр внутри ТТК',
            'внутри мкад вне ттк': 'Внутри МКАД вне ТТК',
            'за мкад': 'За МКАД'
        }
        
        for district_lower in moscow_districts:
            if district_lower in snapshot_text:
                result['district'] = district_map[district_lower]
                break
        
        # Поиск года
        year_match = re.search(r'(\d{4})\s*год', snapshot_text, re.I)
        if year_match:
            year = year_match.group(1)
            if 1900 <= int(year) <= 2030:
                result['year'] = year
        
        return result
        
    except Exception as e:
        print(f"Ошибка при парсинге через MCP: {e}")
        return result


class MCPParserWrapper:
    """Обертка для MCP парсера, которая может использоваться с реальными MCP инструментами"""
    
    def __init__(self):
        self.mcp_tools = None
    
    def set_mcp_tools(self, tools):
        """Установка MCP инструментов"""
        self.mcp_tools = tools
    
    def parse(self, url: str) -> Dict[str, Optional[str]]:
        """Парсинг URL"""
        if not self.mcp_tools:
            raise RuntimeError("MCP инструменты не установлены")
        return parse_with_mcp_browser(url, self.mcp_tools)
