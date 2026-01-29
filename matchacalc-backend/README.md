# MatchaCalc Backend

Backend API для калькулятора доходности коммерческой недвижимости.

## Быстрый старт

### 1. Установка зависимостей

```bash
cd matchacalc-backend
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Настройка окружения

Создайте файл `.env` в корне `matchacalc-backend/`:

```env
DATABASE_URL=postgresql://matchacalc:secret@localhost:5432/matchacalc
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
RATE_LIMIT_GUEST=180
RATE_LIMIT_USER=60
RATE_LIMIT_SUBSCRIBER=10
```

### 3. Запуск БД и Redis

Убедитесь, что PostgreSQL и Redis запущены:

```bash
# PostgreSQL (уже запущен в Docker)
docker ps | grep postgres

# Redis (если нужно запустить)
docker-compose up -d redis
```

### 4. Применение миграций

```bash
source .venv/bin/activate
alembic upgrade head
```

### 5. Загрузка seed данных

```bash
source .venv/bin/activate
python scripts/seed_db.py
```

Это создаст:
- Группы локаций (Москва-Сити, Большой Сити и т.д.)
- Сценарии (Пессимистичный, Базовый, Оптимистичный)
- Администратора: `admin@matchacalc.ru` / `admin123`

### 6. Аккаунты для стаджинга (премиум + админ)

На сервере стаджинга (VPS), в папке бэкенда с `.env`, указывающим на стаджинг-БД:

```bash
cd /root/matchacalc-backend-staging
.venv/bin/python scripts/create_staging_users.py
```

Будут созданы/обновлены:
- **Премиум:** `premium.stagging@commercial.ru` / `StagingFacePremium333WWW###` (подписка developer)
- **Админ:** `admin.stagging@commercial.ru` / `StagingFaceAdmin333WWW###` (вход в админку)

### 7. Загрузка данных рынка

```bash
source .venv/bin/activate
python scripts/load_market_data.py ../market_data_Q4_2025.json
```

Это загрузит:
- 3 отчёта (Nikoliers, NF Group, CBRE) за Q4 2025
- 27 значений рынка (по 9 для каждого отчёта)

### 8. Запуск сервера

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API будет доступен по адресу: http://localhost:8000

## API Endpoints

### Аутентификация
- `POST /api/v1/auth/register` - Регистрация
- `POST /api/v1/auth/login` - Вход
- `GET /api/v1/auth/me` - Информация о текущем пользователе

### Калькулятор
- `POST /api/v1/calc/preview` - Расчёт доходности

### Отчёты и данные
- `GET /api/v1/reports` - Список отчётов
- `GET /api/v1/reports/location-groups` - Группы локаций
- `GET /api/v1/reports/scenarios` - Сценарии

### Админ (требует права администратора)
- `POST /api/v1/admin/reports` - Создание отчёта
- `POST /api/v1/admin/report-values` - Создание значения отчёта
- `POST /api/v1/admin/location-groups` - Создание группы локаций
- `POST /api/v1/admin/scenarios` - Создание сценария

## Документация API

После запуска сервера доступна автоматическая документация:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Загрузка данных рынка

Используйте скрипт для загрузки данных из JSON файла:

```bash
python scripts/load_market_data.py ../market_data_Q4_2025.json
```

Скрипт автоматически:
- Создаст отчёты (если их ещё нет)
- Загрузит все значения рынка
- Обновит существующие значения при повторном запуске

## Структура проекта

```
matchacalc-backend/
├── app/
│   ├── main.py              # Точка входа FastAPI
│   ├── config.py            # Настройки приложения
│   ├── auth/                # Модуль аутентификации
│   ├── calc/                # Модуль калькулятора
│   ├── reports/             # Модуль отчётов
│   ├── admin/               # Админ API
│   ├── ratelimit/           # Rate limiting
│   └── db/                  # Модели БД и подключение
├── alembic/                 # Миграции БД
├── scripts/                 # Вспомогательные скрипты
└── requirements.txt         # Зависимости
```
