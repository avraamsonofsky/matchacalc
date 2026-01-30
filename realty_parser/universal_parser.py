"""
Универсальный парсер с автоматическим выбором метода
"""
import json
from typing import Dict, Optional, Literal
from parser_v1_requests import RequestsParser
from parser_v2_selenium import SeleniumParser
from parser_v3_playwright import PlaywrightParser


class UniversalParser:
    """Универсальный парсер с поддержкой нескольких методов"""
    
    def __init__(self, method: Literal['auto', 'requests', 'selenium', 'playwright'] = 'auto'):
        """
        Инициализация парсера
        
        Args:
            method: Метод парсинга
                - 'auto': автоматический выбор (сначала requests, затем selenium/playwright)
                - 'requests': только requests + BeautifulSoup
                - 'selenium': только Selenium
                - 'playwright': только Playwright
        """
        self.method = method
        self.requests_parser = None
        self.selenium_parser = None
        self.playwright_parser = None
        
        if method in ['auto', 'requests']:
            self.requests_parser = RequestsParser()
        
        if method in ['auto', 'selenium']:
            try:
                self.selenium_parser = SeleniumParser(headless=True)
            except Exception as e:
                print(f"Предупреждение: Selenium недоступен: {e}")
        
        if method in ['auto', 'playwright']:
            try:
                self.playwright_parser = PlaywrightParser(headless=True)
            except Exception as e:
                print(f"Предупреждение: Playwright недоступен: {e}")
    
    def parse(self, url: str) -> Dict[str, Optional[str]]:
        """
        Парсинг URL с автоматическим выбором метода
        
        Args:
            url: URL для парсинга
            
        Returns:
            Словарь с данными: {'price': str, 'area': str, 'district': str, 'year': str}
        """
        if self.method == 'requests':
            return self.requests_parser.parse(url)
        
        elif self.method == 'selenium':
            if not self.selenium_parser:
                raise RuntimeError("Selenium парсер не инициализирован")
            return self.selenium_parser.parse(url)
        
        elif self.method == 'playwright':
            if not self.playwright_parser:
                raise RuntimeError("Playwright парсер не инициализирован")
            return self.playwright_parser.parse(url)
        
        else:  # auto
            # Пробуем сначала requests (быстрее)
            try:
                result = self.requests_parser.parse(url)
                # Проверяем, что получили хотя бы часть данных
                if any([result.get('price'), result.get('area')]):
                    return result
            except Exception as e:
                print(f"Requests парсер не смог обработать: {e}")
            
            # Если requests не сработал, пробуем Selenium
            if self.selenium_parser:
                try:
                    result = self.selenium_parser.parse(url)
                    if any([result.get('price'), result.get('area')]):
                        return result
                except Exception as e:
                    print(f"Selenium парсер не смог обработать: {e}")
            
            # Если Selenium не сработал, пробуем Playwright
            if self.playwright_parser:
                try:
                    result = self.playwright_parser.parse(url)
                    return result
                except Exception as e:
                    print(f"Playwright парсер не смог обработать: {e}")
            
            # Если ничего не сработало, возвращаем пустой результат
            return {'price': None, 'area': None, 'district': None, 'year': None}
    
    def close(self):
        """Закрытие всех парсеров"""
        if self.selenium_parser:
            self.selenium_parser.close()
        if self.playwright_parser:
            self.playwright_parser.close()


def parse_url(url: str, method: str = 'auto') -> Dict[str, Optional[str]]:
    """
    Удобная функция для быстрого парсинга
    
    Args:
        url: URL для парсинга
        method: Метод парсинга ('auto', 'requests', 'selenium', 'playwright')
    
    Returns:
        Словарь с данными
    """
    parser = UniversalParser(method=method)
    try:
        result = parser.parse(url)
        return result
    finally:
        parser.close()


if __name__ == '__main__':
    # Пример использования
    test_urls = [
        'https://lyubertsy.cian.ru/sale/commercial/307487135/?mlSearchSessionGuid=17d51975165d9139f2fab7d2791cfa2a',
        'https://www.avito.ru/moskva/kommercheskaya_nedvizhimost/prodam_ofisnoe_pomeschenie_190.7_m_7816254767?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJOSk9ieWdiaWUzalhTNWROIjt9oMPn_z8AAAA',
        'https://realty.yandex.ru/offer/7567098664232911117/'
    ]
    
    parser = UniversalParser(method='auto')
    
    for url in test_urls:
        print(f"\nПарсинг: {url}")
        result = parser.parse(url)
        print(f"Результат: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    parser.close()
