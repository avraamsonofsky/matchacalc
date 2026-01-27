# Инструкция по загрузке данных в БД MatchaCalc

## Обзор

Подготовлены данные из 3 источников:
- **Nikoliers** (Q4 2024)
- **NF GROUP** (Q1 2025) 
- **CBRE** (H1 2025)

Всего: **27 data points** по 5 районам Москвы и различным классам недвижимости

---

## Процесс загрузки

### Шаг 1: Создание отчётов (MarketReport)

Для каждого провайдера выполните POST-запрос:

#### 1.1 Nikoliers Q4 2024

```bash
curl -X POST http://localhost:8000/api/v1/admin/reports \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "provider": "nikoliers",
    "title": "Обзор рынка коммерческой недвижимости Москвы Q4 2024",
    "period": "2024-Q4",
    "file_url": "https://nikoliers.com/upload/iblock/845/nikoliers-moscow-commercial-2024-q4.pdf",
    "active": true
  }'
```

**Ожидаемый ответ:**
```json
{
  "id": 1,
  "provider": "nikoliers",
  "title": "Обзор рынка коммерческой недвижимости Москвы Q4 2024",
  "period": "2024-Q4",
  "file_url": "https://nikoliers.com/upload/iblock/845/nikoliers-moscow-commercial-2024-q4.pdf",
  "active": true,
  "created_at": "2026-01-19T16:30:00Z"
}
```

**⚠️ Сохраните ID: 1** (понадобится для значений)

---

#### 1.2 NF GROUP Q1 2025

```bash
curl -X POST http://localhost:8000/api/v1/admin/reports \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "provider": "nf_group",
    "title": "Анализ офисного рынка Москвы Q1 2025",
    "period": "2025-Q1",
    "file_url": "https://nf-group.ru/upload/research/moscow-office-market-q1-2025.pdf",
    "active": true
  }'
```

**⚠️ Сохраните ID: 2**

---

#### 1.3 CBRE H1 2025

```bash
curl -X POST http://localhost:8000/api/v1/admin/reports \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "provider": "cbre",
    "title": "Обзор офисного рынка Москвы 2025",
    "period": "2025-H1",
    "file_url": "https://cbre.ru/research/moscow-office-market-2025-h1.pdf",
    "active": true
  }'
```

**⚠️ Сохраните ID: 3**

---

### Шаг 2: Загрузка значений отчётов (MarketReportValues)

Для каждого отчёта загружаем значения по районам и классам. Используйте IDs из Шага 1.

#### Nikoliers (report_id = 1)

##### 1. Москва-Сити, A_Prime
```bash
curl -X POST http://localhost:8000/api/v1/admin/report-values \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "report_id": 1,
    "location_group_id": "moscow_city",
    "property_class": "A_Prime",
    "rent_start": 35000.0,
    "rent_growth_annual": 0.05,
    "price_per_m2_start": 450000.0,
    "price_growth_annual": 0.03,
    "vacancy_rate": 0.08
  }'
```

##### 2. Москва-Сити, A
```json
{
  "report_id": 1,
  "location_group_id": "moscow_city",
  "property_class": "A",
  "rent_start": 28000.0,
  "rent_growth_annual": 0.05,
  "price_per_m2_start": 380000.0,
  "price_growth_annual": 0.03,
  "vacancy_rate": 0.10
}
```

##### 3. Большой Сити, A
```json
{
  "report_id": 1,
  "location_group_id": "big_city",
  "property_class": "A",
  "rent_start": 24000.0,
  "rent_growth_annual": 0.04,
  "price_per_m2_start": 320000.0,
  "price_growth_annual": 0.03,
  "vacancy_rate": 0.12
}
```

##### 4. Большой Сити, B+
```json
{
  "report_id": 1,
  "location_group_id": "big_city",
  "property_class": "B_plus",
  "rent_start": 18000.0,
  "rent_growth_annual": 0.04,
  "price_per_m2_start": 240000.0,
  "price_growth_annual": 0.025,
  "vacancy_rate": 0.15
}
```

##### 5. Центр внутри ТТК, A
```json
{
  "report_id": 1,
  "location_group_id": "center_ttk",
  "property_class": "A",
  "rent_start": 26000.0,
  "rent_growth_annual": 0.045,
  "price_per_m2_start": 400000.0,
  "price_growth_annual": 0.032,
  "vacancy_rate": 0.11
}
```

##### 6. Центр внутри ТТК, B+
```json
{
  "report_id": 1,
  "location_group_id": "center_ttk",
  "property_class": "B_plus",
  "rent_start": 19000.0,
  "rent_growth_annual": 0.04,
  "price_per_m2_start": 260000.0,
  "price_growth_annual": 0.025,
  "vacancy_rate": 0.14
}
```

##### 7. Внутри МКАД вне ТТК, B+
```json
{
  "report_id": 1,
  "location_group_id": "mkad_outside_ttk",
  "property_class": "B_plus",
  "rent_start": 15000.0,
  "rent_growth_annual": 0.035,
  "price_per_m2_start": 200000.0,
  "price_growth_annual": 0.02,
  "vacancy_rate": 0.18
}
```

##### 8. Внутри МКАД вне ТТК, B
```json
{
  "report_id": 1,
  "location_group_id": "mkad_outside_ttk",
  "property_class": "B",
  "rent_start": 12000.0,
  "rent_growth_annual": 0.03,
  "price_per_m2_start": 150000.0,
  "price_growth_annual": 0.018,
  "vacancy_rate": 0.20
}
```

##### 9. За МКАД, B
```json
{
  "report_id": 1,
  "location_group_id": "outside_mkad",
  "property_class": "B",
  "rent_start": 10000.0,
  "rent_growth_annual": 0.03,
  "price_per_m2_start": 120000.0,
  "price_growth_annual": 0.015,
  "vacancy_rate": 0.22
}
```

---

#### NF GROUP (report_id = 2)

##### 1. Москва-Сити, A_Prime
```json
{
  "report_id": 2,
  "location_group_id": "moscow_city",
  "property_class": "A_Prime",
  "rent_start": 37400.0,
  "rent_growth_annual": 0.06,
  "price_per_m2_start": 480000.0,
  "price_growth_annual": 0.035,
  "vacancy_rate": 0.068
}
```

##### 2. Москва-Сити, A
```json
{
  "report_id": 2,
  "location_group_id": "moscow_city",
  "property_class": "A",
  "rent_start": 30000.0,
  "rent_growth_annual": 0.055,
  "price_per_m2_start": 400000.0,
  "price_growth_annual": 0.032,
  "vacancy_rate": 0.088
}
```

##### 3. Большой Сити, A
```json
{
  "report_id": 2,
  "location_group_id": "big_city",
  "property_class": "A",
  "rent_start": 25500.0,
  "rent_growth_annual": 0.045,
  "price_per_m2_start": 340000.0,
  "price_growth_annual": 0.032,
  "vacancy_rate": 0.11
}
```

##### 4. Большой Сити, B+
```json
{
  "report_id": 2,
  "location_group_id": "big_city",
  "property_class": "B_plus",
  "rent_start": 19000.0,
  "rent_growth_annual": 0.042,
  "price_per_m2_start": 260000.0,
  "price_growth_annual": 0.028,
  "vacancy_rate": 0.135
}
```

##### 5. Центр внутри ТТК, A
```json
{
  "report_id": 2,
  "location_group_id": "center_ttk",
  "property_class": "A",
  "rent_start": 28500.0,
  "rent_growth_annual": 0.048,
  "price_per_m2_start": 430000.0,
  "price_growth_annual": 0.035,
  "vacancy_rate": 0.095
}
```

##### 6. Центр внутри ТТК, B+
```json
{
  "report_id": 2,
  "location_group_id": "center_ttk",
  "property_class": "B_plus",
  "rent_start": 20000.0,
  "rent_growth_annual": 0.043,
  "price_per_m2_start": 280000.0,
  "price_growth_annual": 0.027,
  "vacancy_rate": 0.128
}
```

##### 7. Внутри МКАД вне ТТК, B+
```json
{
  "report_id": 2,
  "location_group_id": "mkad_outside_ttk",
  "property_class": "B_plus",
  "rent_start": 16000.0,
  "rent_growth_annual": 0.038,
  "price_per_m2_start": 220000.0,
  "price_growth_annual": 0.024,
  "vacancy_rate": 0.155
}
```

##### 8. Внутри МКАД вне ТТК, B
```json
{
  "report_id": 2,
  "location_group_id": "mkad_outside_ttk",
  "property_class": "B",
  "rent_start": 12500.0,
  "rent_growth_annual": 0.032,
  "price_per_m2_start": 165000.0,
  "price_growth_annual": 0.020,
  "vacancy_rate": 0.175
}
```

##### 9. За МКАД, B
```json
{
  "report_id": 2,
  "location_group_id": "outside_mkad",
  "property_class": "B",
  "rent_start": 10500.0,
  "rent_growth_annual": 0.032,
  "price_per_m2_start": 135000.0,
  "price_growth_annual": 0.018,
  "vacancy_rate": 0.195
}
```

---

#### CBRE (report_id = 3)

##### 1. Москва-Сити, A_Prime
```json
{
  "report_id": 3,
  "location_group_id": "moscow_city",
  "property_class": "A_Prime",
  "rent_start": 38000.0,
  "rent_growth_annual": 0.062,
  "price_per_m2_start": 500000.0,
  "price_growth_annual": 0.038,
  "vacancy_rate": 0.065
}
```

##### 2. Москва-Сити, A
```json
{
  "report_id": 3,
  "location_group_id": "moscow_city",
  "property_class": "A",
  "rent_start": 31000.0,
  "rent_growth_annual": 0.058,
  "price_per_m2_start": 420000.0,
  "price_growth_annual": 0.035,
  "vacancy_rate": 0.082
}
```

##### 3. Большой Сити, A
```json
{
  "report_id": 3,
  "location_group_id": "big_city",
  "property_class": "A",
  "rent_start": 26500.0,
  "rent_growth_annual": 0.048,
  "price_per_m2_start": 360000.0,
  "price_growth_annual": 0.034,
  "vacancy_rate": 0.105
}
```

##### 4. Большой Сити, B+
```json
{
  "report_id": 3,
  "location_group_id": "big_city",
  "property_class": "B_plus",
  "rent_start": 20000.0,
  "rent_growth_annual": 0.045,
  "price_per_m2_start": 280000.0,
  "price_growth_annual": 0.030,
  "vacancy_rate": 0.130
}
```

##### 5. Центр внутри ТТК, A
```json
{
  "report_id": 3,
  "location_group_id": "center_ttk",
  "property_class": "A",
  "rent_start": 29500.0,
  "rent_growth_annual": 0.050,
  "price_per_m2_start": 450000.0,
  "price_growth_annual": 0.036,
  "vacancy_rate": 0.090
}
```

##### 6. Центр внутри ТТК, B+
```json
{
  "report_id": 3,
  "location_group_id": "center_ttk",
  "property_class": "B_plus",
  "rent_start": 21000.0,
  "rent_growth_annual": 0.045,
  "price_per_m2_start": 300000.0,
  "price_growth_annual": 0.029,
  "vacancy_rate": 0.122
}
```

##### 7. Внутри МКАД вне ТТК, B+
```json
{
  "report_id": 3,
  "location_group_id": "mkad_outside_ttk",
  "property_class": "B_plus",
  "rent_start": 17000.0,
  "rent_growth_annual": 0.040,
  "price_per_m2_start": 240000.0,
  "price_growth_annual": 0.026,
  "vacancy_rate": 0.148
}
```

##### 8. Внутри МКАД вне ТТК, B
```json
{
  "report_id": 3,
  "location_group_id": "mkad_outside_ttk",
  "property_class": "B",
  "rent_start": 13500.0,
  "rent_growth_annual": 0.035,
  "price_per_m2_start": 180000.0,
  "price_growth_annual": 0.022,
  "vacancy_rate": 0.168
}
```

##### 9. За МКАД, B
```json
{
  "report_id": 3,
  "location_group_id": "outside_mkad",
  "property_class": "B",
  "rent_start": 11000.0,
  "rent_growth_annual": 0.035,
  "price_per_m2_start": 145000.0,
  "price_growth_annual": 0.020,
  "vacancy_rate": 0.188
}
```

---

## Альтернатива: Batch загрузка через скрипт

Если у тебя есть доступ к Python и ты хочешь загрузить всё автоматически:

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1/admin"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer YOUR_ADMIN_TOKEN"
}

# Загрузить JSON файл с данными
with open("market_reports_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Загрузить отчёты и их значения
for report_block in data["reports"]:
    # 1. Создать отчёт
    report_data = report_block["market_report"]
    resp = requests.post(f"{BASE_URL}/reports", json=report_data, headers=HEADERS)
    report_id = resp.json()["id"]
    print(f"✅ Created report: {report_data['provider']} (ID: {report_id})")
    
    # 2. Загрузить значения
    for value in report_block["market_report_values"]:
        value["report_id"] = report_id
        resp = requests.post(f"{BASE_URL}/report-values", json=value, headers=HEADERS)
        print(f"   ✓ Loaded: {value['location_group_id']} - {value['property_class']}")
```

---

## Проверка загруженных данных

После загрузки проверьте данные:

```bash
# Получить список всех отчётов
curl http://localhost:8000/api/v1/reports \
  -H "Authorization: Bearer YOUR_TOKEN"

# Получить значения конкретного отчёта
curl http://localhost:8000/api/v1/admin/reports/1/values \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## Важные замечания

✅ **Все ставки в рублях:**
- `rent_start` - ₽/м²/месяц
- `price_per_m2_start` - ₽/м²

✅ **Все темпы роста в десятичной дроби:**
- 5% = 0.05
- 4% = 0.04
- 3% = 0.03

✅ **Коэффициент простоя в десятичной дроби:**
- 8% = 0.08
- 10% = 0.10
- 15% = 0.15

✅ **Данные собраны из актуальных источников (Q4 2024 - Q1 2025)**

---

## Контакты и поддержка

Если возникнут проблемы с загрузкой:
- Проверьте токен авторизации
- Убедитесь в корректности всех location_group_id и property_class
- Проверьте формат всех числовых значений
