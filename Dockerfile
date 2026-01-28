FROM python:3.12-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements и установка зависимостей
COPY matchacalc-backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода бэкенда
COPY matchacalc-backend/ ./matchacalc-backend/

# Копирование статических файлов фронтенда в папку static бэкенда
COPY matchacalc-frontend/ ./matchacalc-backend/static/

# Рабочая директория - бэкенд
WORKDIR /app/matchacalc-backend

# Открываем порт
EXPOSE 8000

# Команда запуска
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
