"""
Парсер через requests + BeautifulSoup
Простой и быстрый вариант для статического контента
"""
import re
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from typing import Dict, Optional


class RequestsParser:
    """Парсер на основе requests и BeautifulSoup"""
    
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        })
    
    def parse_cian(self, url: str) -> Dict[str, Optional[str]]:
        """Парсинг данных с Cian.ru"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml')
            
            result = {
                'price': None,
                'area': None,
                'district': None,
                'year': None
            }
            
            # Поиск цены - пробуем разные селекторы
            price_selectors = [
                {'tag': 'span', 'class': re.compile(r'.*price.*', re.I)},
                {'tag': 'div', 'class': re.compile(r'.*price.*', re.I)},
                {'tag': 'meta', 'property': 'product:price:amount'},
                {'tag': 'script', 'type': 'application/ld+json'},
            ]
            
            for selector in price_selectors:
                elements = soup.find_all(**selector)
                for elem in elements:
                    if elem.name == 'script':
                        # Парсинг JSON-LD
                        try:
                            import json
                            data = json.loads(elem.string)
                            if isinstance(data, dict) and 'offers' in data:
                                price = data['offers'].get('price', '')
                                if price:
                                    result['price'] = str(int(price))
                                    break
                        except:
                            pass
                    else:
                        text = elem.get_text() if elem.name != 'meta' else elem.get('content', '')
                        price_match = re.search(r'[\d\s]+', text.replace(' ', ''))
                        if price_match:
                            price = price_match.group().replace(' ', '')
                            if price and len(price) > 4:
                                result['price'] = price
                                break
                if result['price']:
                    break
            
            # Поиск площади
            area_selectors = [
                {'tag': 'span', 'class': re.compile(r'.*area.*', re.I)},
                {'tag': 'div', 'class': re.compile(r'.*area.*', re.I)},
                {'tag': 'span', 'text': re.compile(r'.*м².*', re.I)},
            ]
            
            for selector in area_selectors:
                elements = soup.find_all(**selector)
                for elem in elements:
                    text = elem.get_text()
                    area_match = re.search(r'(\d+(?:[.,]\d+)?)\s*м²', text, re.I)
                    if area_match:
                        area = area_match.group(1).replace(',', '.')
                        result['area'] = str(int(float(area)))
                        break
                if result['area']:
                    break
            
            # Поиск района
            district_keywords = ['район', 'district', 'location', 'адрес']
            page_text = soup.get_text()
            moscow_districts = [
                'Москва-Сити', 'Большой Сити', 'Центр внутри ТТК',
                'Внутри МКАД вне ТТК', 'За МКАД'
            ]
            for district in moscow_districts:
                if district.lower() in page_text.lower():
                    result['district'] = district
                    break
            
            # Поиск года постройки
            year_patterns = [
                r'(\d{4})\s*год',
                r'построен[ая]?\s*в\s*(\d{4})',
                r'год\s*постройки[:\s]+(\d{4})',
                r'ввод\s*в\s*эксплуатацию[:\s]+(\d{4})',
            ]
            
            for pattern in year_patterns:
                match = re.search(pattern, page_text, re.I)
                if match:
                    year = match.group(1)
                    if 1900 <= int(year) <= 2030:
                        result['year'] = year
                        break
            
            return result
            
        except Exception as e:
            print(f"Ошибка при парсинге Cian: {e}")
            return {'price': None, 'area': None, 'district': None, 'year': None}
    
    def parse_avito(self, url: str) -> Dict[str, Optional[str]]:
        """Парсинг данных с Avito.ru"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml')
            
            result = {
                'price': None,
                'area': None,
                'district': None,
                'year': None
            }
            
            # Поиск цены
            price_elem = soup.find('span', {'data-marker': 'item-view/item-price'})
            if not price_elem:
                price_elem = soup.find('span', class_=re.compile(r'.*price.*', re.I))
            
            if price_elem:
                price_text = price_elem.get_text()
                price_match = re.search(r'[\d\s]+', price_text.replace(' ', ''))
                if price_match:
                    result['price'] = price_match.group().replace(' ', '')
            
            # Поиск площади
            params = soup.find_all('li', class_=re.compile(r'.*params.*', re.I))
            for param in params:
                text = param.get_text()
                area_match = re.search(r'(\d+(?:[.,]\d+)?)\s*м²', text, re.I)
                if area_match:
                    area = area_match.group(1).replace(',', '.')
                    result['area'] = str(int(float(area)))
                    break
            
            # Поиск района
            location_elem = soup.find('span', {'data-marker': 'item-view/item-address'})
            if location_elem:
                location_text = location_elem.get_text()
                moscow_districts = [
                    'Москва-Сити', 'Большой Сити', 'Центр внутри ТТК',
                    'Внутри МКАД вне ТТК', 'За МКАД'
                ]
                for district in moscow_districts:
                    if district.lower() in location_text.lower():
                        result['district'] = district
                        break
            
            # Поиск года
            page_text = soup.get_text()
            year_match = re.search(r'(\d{4})\s*год', page_text, re.I)
            if year_match:
                year = year_match.group(1)
                if 1900 <= int(year) <= 2030:
                    result['year'] = year
            
            return result
            
        except Exception as e:
            print(f"Ошибка при парсинге Avito: {e}")
            return {'price': None, 'area': None, 'district': None, 'year': None}
    
    def parse_yandex_realty(self, url: str) -> Dict[str, Optional[str]]:
        """Парсинг данных с Yandex Realty"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml')
            
            result = {
                'price': None,
                'area': None,
                'district': None,
                'year': None
            }
            
            # Поиск цены
            price_elem = soup.find('span', class_=re.compile(r'.*price.*', re.I))
            if price_elem:
                price_text = price_elem.get_text()
                price_match = re.search(r'[\d\s]+', price_text.replace(' ', ''))
                if price_match:
                    result['price'] = price_match.group().replace(' ', '')
            
            # Поиск площади
            area_elem = soup.find('span', text=re.compile(r'.*м².*', re.I))
            if area_elem:
                text = area_elem.get_text()
                area_match = re.search(r'(\d+(?:[.,]\d+)?)\s*м²', text, re.I)
                if area_match:
                    area = area_match.group(1).replace(',', '.')
                    result['area'] = str(int(float(area)))
            
            # Поиск района
            location_elem = soup.find('div', class_=re.compile(r'.*location.*', re.I))
            if location_elem:
                location_text = location_elem.get_text()
                moscow_districts = [
                    'Москва-Сити', 'Большой Сити', 'Центр внутри ТТК',
                    'Внутри МКАД вне ТТК', 'За МКАД'
                ]
                for district in moscow_districts:
                    if district.lower() in location_text.lower():
                        result['district'] = district
                        break
            
            # Поиск года
            page_text = soup.get_text()
            year_match = re.search(r'(\d{4})\s*год', page_text, re.I)
            if year_match:
                year = year_match.group(1)
                if 1900 <= int(year) <= 2030:
                    result['year'] = year
            
            return result
            
        except Exception as e:
            print(f"Ошибка при парсинге Yandex Realty: {e}")
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
