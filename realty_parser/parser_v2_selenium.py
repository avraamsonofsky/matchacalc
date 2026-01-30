"""
Парсер через Selenium
Для динамического контента, который загружается через JavaScript
"""
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from typing import Dict, Optional


class SeleniumParser:
    """Парсер на основе Selenium для динамического контента"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        self._init_driver()
    
    def _init_driver(self):
        """Инициализация драйвера"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
        except Exception as e:
            print(f"Ошибка инициализации Selenium: {e}")
            print("Убедитесь, что установлен ChromeDriver")
            raise
    
    def parse_cian(self, url: str) -> Dict[str, Optional[str]]:
        """Парсинг данных с Cian.ru через Selenium"""
        try:
            self.driver.get(url)
            time.sleep(3)  # Ждем загрузки динамического контента
            
            result = {
                'price': None,
                'area': None,
                'district': None,
                'year': None
            }
            
            # Поиск цены
            price_selectors = [
                "//span[contains(@class, 'price')]",
                "//div[contains(@class, 'price')]",
                "//span[contains(text(), '₽')]",
            ]
            
            for selector in price_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        text = elem.text
                        price_match = re.search(r'[\d\s]+', text.replace(' ', ''))
                        if price_match:
                            price = price_match.group().replace(' ', '')
                            if price and len(price) > 4:
                                result['price'] = price
                                break
                    if result['price']:
                        break
                except:
                    continue
            
            # Поиск площади
            area_selectors = [
                "//span[contains(text(), 'м²')]",
                "//div[contains(text(), 'м²')]",
            ]
            
            for selector in area_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        text = elem.text
                        area_match = re.search(r'(\d+(?:[.,]\d+)?)\s*м²', text, re.I)
                        if area_match:
                            area = area_match.group(1).replace(',', '.')
                            result['area'] = str(int(float(area)))
                            break
                    if result['area']:
                        break
                except:
                    continue
            
            # Поиск района
            page_text = self.driver.page_source
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
            
            return result
            
        except Exception as e:
            print(f"Ошибка при парсинге Cian (Selenium): {e}")
            return {'price': None, 'area': None, 'district': None, 'year': None}
    
    def parse_avito(self, url: str) -> Dict[str, Optional[str]]:
        """Парсинг данных с Avito.ru через Selenium"""
        try:
            self.driver.get(url)
            time.sleep(3)
            
            result = {
                'price': None,
                'area': None,
                'district': None,
                'year': None
            }
            
            # Поиск цены
            try:
                price_elem = self.driver.find_element(By.CSS_SELECTOR, '[data-marker="item-view/item-price"]')
                price_text = price_elem.text
                price_match = re.search(r'[\d\s]+', price_text.replace(' ', ''))
                if price_match:
                    result['price'] = price_match.group().replace(' ', '')
            except:
                pass
            
            # Поиск площади
            try:
                params = self.driver.find_elements(By.CSS_SELECTOR, '[class*="params"]')
                for param in params:
                    text = param.text
                    area_match = re.search(r'(\d+(?:[.,]\d+)?)\s*м²', text, re.I)
                    if area_match:
                        area = area_match.group(1).replace(',', '.')
                        result['area'] = str(int(float(area)))
                        break
            except:
                pass
            
            # Поиск района
            try:
                location_elem = self.driver.find_element(By.CSS_SELECTOR, '[data-marker="item-view/item-address"]')
                location_text = location_elem.text
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
            page_text = self.driver.page_source
            year_match = re.search(r'(\d{4})\s*год', page_text, re.I)
            if year_match:
                year = year_match.group(1)
                if 1900 <= int(year) <= 2030:
                    result['year'] = year
            
            return result
            
        except Exception as e:
            print(f"Ошибка при парсинге Avito (Selenium): {e}")
            return {'price': None, 'area': None, 'district': None, 'year': None}
    
    def parse_yandex_realty(self, url: str) -> Dict[str, Optional[str]]:
        """Парсинг данных с Yandex Realty через Selenium"""
        try:
            self.driver.get(url)
            time.sleep(3)
            
            result = {
                'price': None,
                'area': None,
                'district': None,
                'year': None
            }
            
            # Поиск цены
            try:
                price_elem = self.driver.find_element(By.CSS_SELECTOR, '[class*="price"]')
                price_text = price_elem.text
                price_match = re.search(r'[\d\s]+', price_text.replace(' ', ''))
                if price_match:
                    result['price'] = price_match.group().replace(' ', '')
            except:
                pass
            
            # Поиск площади
            try:
                area_elems = self.driver.find_elements(By.XPATH, "//span[contains(text(), 'м²')]")
                for elem in area_elems:
                    text = elem.text
                    area_match = re.search(r'(\d+(?:[.,]\d+)?)\s*м²', text, re.I)
                    if area_match:
                        area = area_match.group(1).replace(',', '.')
                        result['area'] = str(int(float(area)))
                        break
            except:
                pass
            
            # Поиск района
            page_text = self.driver.page_source
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
            
            return result
            
        except Exception as e:
            print(f"Ошибка при парсинге Yandex Realty (Selenium): {e}")
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
        """Закрытие драйвера"""
        if self.driver:
            self.driver.quit()
