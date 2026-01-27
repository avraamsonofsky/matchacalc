# Инструкция по запуску MatchaCalc через Docker

## Статус Docker

✅ Docker установлен и работает  
✅ PostgreSQL контейнер уже запущен (`postgres-matchacalc`)  
✅ Docker Compose файл создан и валиден

## Быстрый старт

### Вариант 1: Запуск всех сервисов через docker-compose

```bash
cd /home/nikit/matchacalc

# Запустить все сервисы (postgres, redis, backend)
docker-compose up -d

# Проверить статус
docker-compose ps

# Посмотреть логи бэкенда
docker-compose logs -f backend
```

### Вариант 2: Использовать существующий PostgreSQL

Если PostgreSQL уже запущен отдельно, можно запустить только Redis и Backend:

```bash
cd /home/nikit/matchacalc

# Запустить только redis и backend
docker-compose up -d redis backend

# Или запустить всё - docker-compose сам определит, что postgres уже есть
docker-compose up -d
```

## Проверка работы

После запуска бэкенд будет доступен по адресу:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/

## Остановка

```bash
# Остановить все сервисы
docker-compose down

# Остановить и удалить volumes (⚠️ удалит данные БД)
docker-compose down -v
```

## Пересборка после изменений

```bash
# Пересобрать образ бэкенда
docker-compose build backend

# Перезапустить с новой сборкой
docker-compose up -d --build backend
```

## Переменные окружения

Все переменные окружения заданы в `docker-compose.yml`. Для локальной разработки можно создать `.env` файл в `matchacalc-backend/` (см. `.env.example`).

## Проблемы и решения

### Порт 8000 уже занят
```bash
# Найти процесс, использующий порт
lsof -i :8000

# Или изменить порт в docker-compose.yml
ports:
  - "8001:8000"  # Внешний:Внутренний
```

### PostgreSQL уже запущен отдельно
Docker-compose попытается создать новый контейнер. Можно:
1. Остановить существующий: `docker stop postgres-matchacalc`
2. Или использовать существующий, изменив `docker-compose.yml`

### Ошибки подключения к БД
Проверьте, что:
- PostgreSQL контейнер запущен и здоров
- Переменная `DATABASE_URL` правильная
- Пароль и пользователь совпадают

```bash
# Проверить здоровье PostgreSQL
docker exec postgres-matchacalc pg_isready -U matchacalc
```
