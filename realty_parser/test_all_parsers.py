"""
Комплексное тестирование всех вариантов парсеров
Включая тестирование через MCP инструменты
"""
import json
import sys
from typing import Dict, Optional

# Тестовые URL
TEST_URLS = {
    'cian': 'https://lyubertsy.cian.ru/sale/commercial/307487135/?mlSearchSessionGuid=17d51975165d9139f2fab7d2791cfa2a',
    'avito': 'https://www.avito.ru/moskva/kommercheskaya_nedvizhimost/prodam_ofisnoe_pomeschenie_190.7_m_7816254767?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJOSk9ieWdiaWUzalhTNWROIjt9oMPn_z8AAAA',
    'yandex': 'https://realty.yandex.ru/offer/7567098664232911117/'
}


def test_requests():
    """Тест парсера на requests"""
    print("\n" + "="*60)
    print("ТЕСТ: Requests + BeautifulSoup Parser")
    print("="*60)
    
    try:
        from parser_v1_requests import RequestsParser
        parser = RequestsParser()
        results = {}
        
        for site, url in TEST_URLS.items():
            print(f"\nПарсинг {site.upper()}: {url[:60]}...")
            try:
                result = parser.parse(url)
                results[site] = result
                print(f"  Цена: {result.get('price', 'N/A')}")
                print(f"  Площадь: {result.get('area', 'N/A')}")
                print(f"  Район: {result.get('district', 'N/A')}")
                print(f"  Год: {result.get('year', 'N/A')}")
            except Exception as e:
                print(f"  Ошибка: {e}")
                results[site] = {'error': str(e)}
        
        return results
    except ImportError as e:
        print(f"Ошибка импорта: {e}")
        return {}


def test_selenium():
    """Тест парсера на Selenium"""
    print("\n" + "="*60)
    print("ТЕСТ: Selenium Parser")
    print("="*60)
    
    try:
        from parser_v2_selenium import SeleniumParser
        parser = SeleniumParser(headless=True)
        results = {}
        
        for site, url in TEST_URLS.items():
            print(f"\nПарсинг {site.upper()}: {url[:60]}...")
            try:
                result = parser.parse(url)
                results[site] = result
                print(f"  Цена: {result.get('price', 'N/A')}")
                print(f"  Площадь: {result.get('area', 'N/A')}")
                print(f"  Район: {result.get('district', 'N/A')}")
                print(f"  Год: {result.get('year', 'N/A')}")
            except Exception as e:
                print(f"  Ошибка: {e}")
                results[site] = {'error': str(e)}
        
        parser.close()
        return results
    except Exception as e:
        print(f"Ошибка: {e}")
        return {}


def test_playwright():
    """Тест парсера на Playwright"""
    print("\n" + "="*60)
    print("ТЕСТ: Playwright Parser")
    print("="*60)
    
    try:
        from parser_v3_playwright import PlaywrightParser
        parser = PlaywrightParser(headless=True)
        results = {}
        
        for site, url in TEST_URLS.items():
            print(f"\nПарсинг {site.upper()}: {url[:60]}...")
            try:
                result = parser.parse(url)
                results[site] = result
                print(f"  Цена: {result.get('price', 'N/A')}")
                print(f"  Площадь: {result.get('area', 'N/A')}")
                print(f"  Район: {result.get('district', 'N/A')}")
                print(f"  Год: {result.get('year', 'N/A')}")
            except Exception as e:
                print(f"  Ошибка: {e}")
                results[site] = {'error': str(e)}
        
        parser.close()
        return results
    except Exception as e:
        print(f"Ошибка: {e}")
        return {}


def test_mcp_demo():
    """Демонстрация MCP парсера (требует MCP инструменты)"""
    print("\n" + "="*60)
    print("ТЕСТ: MCP Parser (демонстрация)")
    print("="*60)
    print("MCP парсер требует вызова в контексте с доступом к MCP инструментам")
    print("Для реального использования см. примеры в parser_v4_mcp_impl.py")
    
    results = {}
    for site in TEST_URLS.keys():
        results[site] = {
            'price': None,
            'area': None,
            'district': None,
            'year': None,
            'note': 'Требует MCP инструменты'
        }
    
    return results


def compare_results(all_results: dict):
    """Сравнение результатов всех парсеров"""
    print("\n" + "="*60)
    print("СРАВНЕНИЕ РЕЗУЛЬТАТОВ")
    print("="*60)
    
    for site in TEST_URLS.keys():
        print(f"\n{site.upper()}:")
        for parser_name, parser_results in all_results.items():
            if site in parser_results:
                result = parser_results[site]
                print(f"  {parser_name}:")
                if 'error' in result:
                    print(f"    ❌ Ошибка: {result['error']}")
                elif 'note' in result:
                    print(f"    ℹ️  {result['note']}")
                else:
                    price = result.get('price', 'N/A')
                    area = result.get('area', 'N/A')
                    district = result.get('district', 'N/A')
                    year = result.get('year', 'N/A')
                    
                    status = "✅" if any([price != 'N/A', area != 'N/A']) else "⚠️"
                    print(f"    {status} Цена: {price}, Площадь: {area}, Район: {district}, Год: {year}")


def main():
    """Главная функция тестирования"""
    print("="*60)
    print("ТЕСТИРОВАНИЕ ВСЕХ ВАРИАНТОВ ПАРСЕРОВ")
    print("="*60)
    
    all_results = {}
    
    # Тест Requests
    try:
        all_results['requests'] = test_requests()
    except Exception as e:
        print(f"Ошибка теста Requests: {e}")
        all_results['requests'] = {'error': str(e)}
    
    # Тест Selenium (может быть пропущен, если не установлен)
    try:
        all_results['selenium'] = test_selenium()
    except Exception as e:
        print(f"Selenium недоступен: {e}")
        all_results['selenium'] = {'error': str(e)}
    
    # Тест Playwright (может быть пропущен, если не установлен)
    try:
        all_results['playwright'] = test_playwright()
    except Exception as e:
        print(f"Playwright недоступен: {e}")
        all_results['playwright'] = {'error': str(e)}
    
    # Демо MCP
    all_results['mcp'] = test_mcp_demo()
    
    # Сравнение результатов
    compare_results(all_results)
    
    # Сохранение результатов
    try:
        with open('test_results.json', 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print("\n✅ Результаты сохранены в test_results.json")
    except Exception as e:
        print(f"\n⚠️  Не удалось сохранить результаты: {e}")
    
    return all_results


if __name__ == '__main__':
    main()
