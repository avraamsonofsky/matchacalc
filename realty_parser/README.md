# Универсальный парсер данных недвижимости

Парсер для извлечения данных (цена, площадь, район, год) с сайтов:
- Cian.ru
- Avito.ru
- Yandex Realty

## Реализованные варианты

1. **parser_v1_requests.py** - Парсинг через requests + BeautifulSoup
   - Быстрый и легковесный
   - Подходит для статического контента
   - Не требует дополнительных зависимостей (кроме библиотек)

2. **parser_v2_selenium.py** - Парсинг через Selenium
   - Подходит для динамического контента
   - Требует установки ChromeDriver
   - Медленнее, но надежнее для JS-контента

3. **parser_v3_playwright.py** - Парсинг через Playwright
   - Современная альтернатива Selenium
   - Лучшая поддержка современных веб-приложений
   - Требует установки браузеров Playwright

4. **parser_v4_mcp.py** - Парсинг через MCP сервер
   - Использует Model Context Protocol
   - Требует настройки MCP сервера

5. **universal_parser.py** - Универсальный парсер
   - Автоматический выбор метода
   - Пробует методы по очереди при неудаче

## Установка

```bash
# Установка зависимостей
pip install -r requirements.txt

# Для Playwright требуется установка браузеров
playwright install chromium

# Для Selenium требуется ChromeDriver
# Установите ChromeDriver в PATH или используйте webdriver-manager
```

## Использование

### Простое использование

```python
from universal_parser import parse_url

# Автоматический выбор метода
result = parse_url('https://lyubertsy.cian.ru/sale/commercial/307487135/')
print(result)
# {'price': '50000000', 'area': '150', 'district': 'Внутри МКАД вне ТТК', 'year': '2020'}
```

### Использование конкретного метода

```python
from universal_parser import UniversalParser

parser = UniversalParser(method='requests')  # или 'selenium', 'playwright'
result = parser.parse('https://www.avito.ru/...')
parser.close()
```

### Тестирование всех методов

```bash
python test_parsers.py
```

## Структура данных

Парсер возвращает словарь с полями:
- `price` - цена в рублях (строка, только цифры)
- `area` - площадь в м² (строка)
- `district` - район Москвы (один из: "Москва-Сити", "Большой Сити", "Центр внутри ТТК", "Внутри МКАД вне ТТК", "За МКАД")
- `year` - год постройки/разрешения на ввод (строка, 4 цифры)

## Примечания

- Парсеры могут требовать доработки селекторов под актуальную структуру сайтов
- Некоторые сайты могут блокировать автоматические запросы
- Рекомендуется использовать прокси и ротацию User-Agent для продакшена
- Для MCP парсера требуется дополнительная настройка MCP сервера
