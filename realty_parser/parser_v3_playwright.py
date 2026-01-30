"""
Парсер через Playwright
Современная альтернатива Selenium с лучшей поддержкой динамического контента
"""
import re
from playwright.sync_api import sync_playwright, Browser, Page
from typing import Dict, Optional


class PlaywrightParser:
    """Парсер на основе Playwright"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self._init_browser()
    
    def _init_browser(self):
        """Инициализация браузера"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
    
    def _get_page(self) -> Page:
        """Получение новой страницы"""
        context = self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        return context.new_page()
    
    def parse_cian(self, url: str) -> Dict[str, Optional[str]]:
        """Парсинг данных с Cian.ru через Playwright"""
        page = self._get_page()
        try:
            # Увеличиваем таймаут и меняем условие ожидания
            page.goto(url, wait_until='domcontentloaded', timeout=60000)
            page.wait_for_timeout(5000)  # Даем время на догрузку JS
            
            result = {
                'price': None,
                'area': None,
                'district': None,
                'year': None
            }
            
            # Поиск цены
            price_selectors = [
                'span[data-mark="MainPrice"]',
                'span[class*="price"]',
                'div[class*="price"]',
                'span:has-text("₽")',
            ]
            
            for selector in price_selectors:
                try:
                    elements = page.query_selector_all(selector)
                    for elem in elements:
                        text = elem.inner_text()
                        # Убираем все кроме цифр
                        clean_text = re.sub(r'[^\d]', '', text)
                        if clean_text and len(clean_text) > 4:
                            result['price'] = clean_text
                            break
                    if result['price']:
                        break
                except:
                    continue
            
            # Поиск площади
            # Сначала ищем в заголовке или специфических блоках
            title_text = page.title()
            area_match = re.search(r'(\d+(?:[.,]\d+)?)\s*м²', title_text, re.I)
            if area_match:
                area = area_match.group(1).replace(',', '.')
                result['area'] = str(int(float(area)))
            
            if not result['area']:
                area_elements = page.query_selector_all('text=/\\d+[.,]?\\d*\\s*м²/i')
                for elem in area_elements:
                    text = elem.inner_text()
                    area_match = re.search(r'(\d+(?:[.,]\d+)?)\s*м²', text, re.I)
                    if area_match:
                        area = area_match.group(1).replace(',', '.')
                        result['area'] = str(int(float(area)))
                        break
            
            # Поиск района
            page_text = page.content()
            moscow_districts = [
                'Москва-Сити', 'Большой Сити', 'Центр внутри ТТК',
                'Внутри МКАД вне ТТК', 'За МКАД'
            ]
            for district in moscow_districts:
                if district.lower() in page_text.lower():
                    result['district'] = district
                    break
            
            # Поиск года
            year_match = re.search(r'(\d{4})\s*год', page_text, re.I)
            if year_match:
                year = year_match.group(1)
                if 1900 <= int(year) <= 2030:
                    result['year'] = year
            
            page.close()
            return result
            
        except Exception as e:
            print(f"Ошибка при парсинге Cian (Playwright): {e}")
            page.close()
            return {'price': None, 'area': None, 'district': None, 'year': None}
    
    def parse_avito(self, url: str) -> Dict[str, Optional[str]]:
        """Парсинг данных с Avito.ru через Playwright"""
        page = self._get_page()
        try:
            # Используем domcontentloaded для скорости и надежности
            page.goto(url, wait_until='domcontentloaded', timeout=60000)
            page.wait_for_timeout(5000)
            
            # Проверка на блокировку
            if "Доступ ограничен" in page.title():
                print("Avito blocked IP")
                page.close()
                return {'price': None, 'area': None, 'district': None, 'year': None}
            
            result = {
                'price': None,
                'area': None,
                'district': None,
                'year': None
            }
            
            # Поиск цены
            try:
                price_elem = page.query_selector('[data-marker="item-view/item-price"]')
                if price_elem:
                    price_text = price_elem.inner_text()
                    price_match = re.search(r'[\d\s]+', price_text.replace(' ', ''))
                    if price_match:
                        result['price'] = price_match.group().replace(' ', '')
            except:
                pass
            
            # Поиск площади
            try:
                params = page.query_selector_all('[class*="params"]')
                for param in params:
                    text = param.inner_text()
                    area_match = re.search(r'(\d+(?:[.,]\d+)?)\s*м²', text, re.I)
                    if area_match:
                        area = area_match.group(1).replace(',', '.')
                        result['area'] = str(int(float(area)))
                        break
            except:
                pass
            
            # Поиск района
            try:
                location_elem = page.query_selector('[data-marker="item-view/item-address"]')
                if location_elem:
                    location_text = location_elem.inner_text()
                    moscow_districts = [
                        'Москва-Сити', 'Большой Сити', 'Центр внутри ТТК',
                        'Внутри МКАД вне ТТК', 'За МКАД'
                    ]
                    for district in moscow_districts:
                        if district.lower() in location_text.lower():
                            result['district'] = district
                            break
            except:
                pass
            
            # Поиск года
            page_text = page.content()
            year_match = re.search(r'(\d{4})\s*год', page_text, re.I)
            if year_match:
                year = year_match.group(1)
                if 1900 <= int(year) <= 2030:
                    result['year'] = year
            
            page.close()
            return result
            
        except Exception as e:
            print(f"Ошибка при парсинге Avito (Playwright): {e}")
            page.close()
            return {'price': None, 'area': None, 'district': None, 'year': None}
    
    def parse_yandex_realty(self, url: str) -> Dict[str, Optional[str]]:
        """Парсинг данных с Yandex Realty через Playwright"""
        page = self._get_page()
        try:
            page.goto(url, wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(2000)
            
            result = {
                'price': None,
                'area': None,
                'district': None,
                'year': None
            }
            
            # Поиск цены
            try:
                price_elem = page.query_selector('[class*="price"]')
                if price_elem:
                    price_text = price_elem.inner_text()
                    price_match = re.search(r'[\d\s]+', price_text.replace(' ', ''))
                    if price_match:
                        result['price'] = price_match.group().replace(' ', '')
            except:
                pass
            
            # Поиск площади
            try:
                area_elements = page.query_selector_all('text=/\\d+[.,]?\\d*\\s*м²/i')
                for elem in area_elements:
                    text = elem.inner_text()
                    area_match = re.search(r'(\d+(?:[.,]\d+)?)\s*м²', text, re.I)
                    if area_match:
                        area = area_match.group(1).replace(',', '.')
                        result['area'] = str(int(float(area)))
                        break
            except:
                pass
            
            # Поиск района
            page_text = page.content()
            moscow_districts = [
                'Москва-Сити', 'Большой Сити', 'Центр внутри ТТК',
                'Внутри МКАД вне ТТК', 'За МКАД'
            ]
            for district in moscow_districts:
                if district.lower() in page_text.lower():
                    result['district'] = district
                    break
            
            # Поиск года
            year_match = re.search(r'(\d{4})\s*год', page_text, re.I)
            if year_match:
                year = year_match.group(1)
                if 1900 <= int(year) <= 2030:
                    result['year'] = year
            
            page.close()
            return result
            
        except Exception as e:
            print(f"Ошибка при парсинге Yandex Realty (Playwright): {e}")
            page.close()
            return {'price': None, 'area': None, 'district': None, 'year': None}
    
    def parse(self, url: str) -> Dict[str, Optional[str]]:
        """Универсальный метод парсинга"""
        if 'cian.ru' in url:
            return self.parse_cian(url)
        elif 'avito.ru' in url:
            return self.parse_avito(url)
        elif 'yandex.ru' in url or 'realty.yandex.ru' in url:
            return self.parse_yandex_realty(url)
        else:
            raise ValueError(f"Неподдерживаемый сайт: {url}")
    
    def close(self):
        """Закрытие браузера"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
