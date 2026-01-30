# Инструкция по использованию парсеров

## Быстрый старт

### 1. Установка зависимостей

```bash
cd realty_parser
pip install -r requirements.txt

# Для Playwright (опционально)
playwright install chromium

# Для Selenium требуется ChromeDriver
# Установите ChromeDriver в PATH
```

### 2. Простое использование

```python
from universal_parser import parse_url

# Автоматический выбор метода
result = parse_url('https://lyubertsy.cian.ru/sale/commercial/307487135/')
print(result)
```

### 3. Использование конкретного метода

```python
from parser_v1_requests import RequestsParser

parser = RequestsParser()
result = parser.parse('https://www.avito.ru/...')
```

## Варианты парсеров

### 1. Requests + BeautifulSoup (parser_v1_requests.py)

**Преимущества:**
- Быстрый и легковесный
- Не требует браузера
- Минимальные зависимости

**Недостатки:**
- Не работает с динамическим контентом (JavaScript)
- Может не получить данные, если они загружаются через JS

**Использование:**
```python
from parser_v1_requests import RequestsParser

parser = RequestsParser()
result = parser.parse(url)
```

### 2. Selenium (parser_v2_selenium.py)

**Преимущества:**
- Работает с динамическим контентом
- Полная поддержка JavaScript
- Надежный для сложных сайтов

**Недостатки:**
- Требует ChromeDriver
- Медленнее, чем requests
- Больше потребление ресурсов

**Использование:**
```python
from parser_v2_selenium import SeleniumParser

parser = SeleniumParser(headless=True)
result = parser.parse(url)
parser.close()
```

### 3. Playwright (parser_v3_playwright.py)

**Преимущества:**
- Современная альтернатива Selenium
- Лучшая поддержка современных веб-приложений
- Более стабильный

**Недостатки:**
- Требует установки браузеров
- Медленнее, чем requests

**Использование:**
```python
from parser_v3_playwright import PlaywrightParser

parser = PlaywrightParser(headless=True)
result = parser.parse(url)
parser.close()
```

### 4. MCP Parser (parser_v4_mcp.py, mcp_parser_real.py)

**Преимущества:**
- Использует Model Context Protocol
- Интеграция с AI-инструментами
- Может использовать браузерные возможности MCP

**Недостатки:**
- Требует настройки MCP сервера
- Зависит от доступности MCP инструментов

**Использование:**
```python
# Требует доступ к MCP инструментам
from mcp_parser_real import parse_url_with_mcp
from mcp_cursor-ide-browser import browser_navigate, browser_snapshot

result = parse_url_with_mcp(url, browser_navigate, browser_snapshot)
```

## Тестирование

### Запуск всех тестов

```bash
python test_all_parsers.py
```

Этот скрипт протестирует все доступные парсеры на тестовых URL и сохранит результаты в `test_results.json`.

### Тестирование конкретного парсера

```bash
# Только requests
python -c "from parser_v1_requests import RequestsParser; p = RequestsParser(); print(p.parse('URL'))"

# Только Selenium
python -c "from parser_v2_selenium import SeleniumParser; p = SeleniumParser(); print(p.parse('URL')); p.close()"
```

## Структура данных

Все парсеры возвращают словарь с одинаковой структурой:

```python
{
    'price': '50000000',      # Цена в рублях (строка, только цифры)
    'area': '150',            # Площадь в м² (строка)
    'district': 'Внутри МКАД вне ТТК',  # Район Москвы
    'year': '2020'            # Год постройки/разрешения на ввод
}
```

### Возможные значения district:
- "Москва-Сити"
- "Большой Сити"
- "Центр внутри ТТК"
- "Внутри МКАД вне ТТК"
- "За МКАД"

## Рекомендации

1. **Для быстрого парсинга статических страниц:** используйте `RequestsParser`
2. **Для динамического контента:** используйте `SeleniumParser` или `PlaywrightParser`
3. **Для автоматического выбора:** используйте `UniversalParser` с методом `'auto'`
4. **Для интеграции с AI:** используйте MCP парсер

## Обработка ошибок

Все парсеры возвращают словарь с `None` значениями при ошибках:

```python
result = parser.parse(url)
if not result.get('price'):
    print("Не удалось извлечь цену")
```

## Примечания

- Парсеры могут требовать доработки селекторов под актуальную структуру сайтов
- Некоторые сайты могут блокировать автоматические запросы
- Рекомендуется использовать прокси и ротацию User-Agent для продакшена
- Для MCP парсера требуется дополнительная настройка MCP сервера
