"""
Тестирование всех вариантов парсеров
"""
import json
from parser_v1_requests import RequestsParser
from parser_v2_selenium import SeleniumParser
from parser_v3_playwright import PlaywrightParser
from parser_v4_mcp import parse_with_mcp_tools


# Тестовые URL
TEST_URLS = {
    'cian': 'https://lyubertsy.cian.ru/sale/commercial/307487135/?mlSearchSessionGuid=17d51975165d9139f2fab7d2791cfa2a',
    'avito': 'https://www.avito.ru/moskva/kommercheskaya_nedvizhimost/prodam_ofisnoe_pomeschenie_190.7_m_7816254767?context=H4sIAAAAAAAA_wE_AMD_YToyOntzOjEzOiJsb2NhbFByaW9yaXR5IjtiOjA7czoxOiJ4IjtzOjE2OiJOSk9ieWdiaWUzalhTNWROIjt9oMPn_z8AAAA',
    'yandex': 'https://realty.yandex.ru/offer/7567098664232911117/'
}


def test_requests_parser():
    """Тест парсера на requests"""
    print("\n" + "="*60)
    print("ТЕСТ: Requests + BeautifulSoup Parser")
    print("="*60)
    
    parser = RequestsParser()
    results = {}
    
    for site, url in TEST_URLS.items():
        print(f"\nПарсинг {site.upper()}: {url}")
        try:
            result = parser.parse(url)
            results[site] = result
            print(f"Результат: {json.dumps(result, ensure_ascii=False, indent=2)}")
        except Exception as e:
            print(f"Ошибка: {e}")
            results[site] = {'error': str(e)}
    
    return results


def test_selenium_parser():
    """Тест парсера на Selenium"""
    print("\n" + "="*60)
    print("ТЕСТ: Selenium Parser")
    print("="*60)
    
    try:
        parser = SeleniumParser(headless=True)
        results = {}
        
        for site, url in TEST_URLS.items():
            print(f"\nПарсинг {site.upper()}: {url}")
            try:
                result = parser.parse(url)
                results[site] = result
                print(f"Результат: {json.dumps(result, ensure_ascii=False, indent=2)}")
            except Exception as e:
                print(f"Ошибка: {e}")
                results[site] = {'error': str(e)}
        
        parser.close()
        return results
    except Exception as e:
        print(f"Ошибка инициализации Selenium: {e}")
        return {'error': str(e)}


def test_playwright_parser():
    """Тест парсера на Playwright"""
    print("\n" + "="*60)
    print("ТЕСТ: Playwright Parser")
    print("="*60)
    
    try:
        parser = PlaywrightParser(headless=True)
        results = {}
        
        for site, url in TEST_URLS.items():
            print(f"\nПарсинг {site.upper()}: {url}")
            try:
                result = parser.parse(url)
                results[site] = result
                print(f"Результат: {json.dumps(result, ensure_ascii=False, indent=2)}")
            except Exception as e:
                print(f"Ошибка: {e}")
                results[site] = {'error': str(e)}
        
        parser.close()
        return results
    except Exception as e:
        print(f"Ошибка инициализации Playwright: {e}")
        return {'error': str(e)}


def test_mcp_parser():
    """Тест парсера через MCP"""
    print("\n" + "="*60)
    print("ТЕСТ: MCP Parser")
    print("="*60)
    
    results = {}
    
    for site, url in TEST_URLS.items():
        print(f"\nПарсинг {site.upper()}: {url}")
        try:
            result = parse_with_mcp_tools(url)
            results[site] = result
            print(f"Результат: {json.dumps(result, ensure_ascii=False, indent=2)}")
        except Exception as e:
            print(f"Ошибка: {e}")
            results[site] = {'error': str(e)}
    
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
                    print(f"    Ошибка: {result['error']}")
                else:
                    print(f"    Цена: {result.get('price', 'N/A')}")
                    print(f"    Площадь: {result.get('area', 'N/A')}")
                    print(f"    Район: {result.get('district', 'N/A')}")
                    print(f"    Год: {result.get('year', 'N/A')}")


if __name__ == '__main__':
    all_results = {}
    
    # Тест Requests
    try:
        all_results['requests'] = test_requests_parser()
    except Exception as e:
        print(f"Ошибка теста Requests: {e}")
        all_results['requests'] = {'error': str(e)}
    
    # Тест Selenium
    try:
        all_results['selenium'] = test_selenium_parser()
    except Exception as e:
        print(f"Ошибка теста Selenium: {e}")
        all_results['selenium'] = {'error': str(e)}
    
    # Тест Playwright
    try:
        all_results['playwright'] = test_playwright_parser()
    except Exception as e:
        print(f"Ошибка теста Playwright: {e}")
        all_results['playwright'] = {'error': str(e)}
    
    # Тест MCP (требует специальной настройки)
    # all_results['mcp'] = test_mcp_parser()
    
    # Сравнение результатов
    compare_results(all_results)
    
    # Сохранение результатов
    with open('test_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print("\nРезультаты сохранены в test_results.json")
