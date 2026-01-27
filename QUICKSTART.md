# Быстрый запуск MatchaCalc

## Бэкенд (Терминал 1)

```bash
cd matchacalc-backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API: http://localhost:8000  
Docs: http://localhost:8000/docs

## Фронтенд (Терминал 2)

```bash
cd matchacalc-frontend
python3 -m http.server 8080
```

Фронтенд: http://localhost:8080

## Если нужно загрузить данные рынка

```bash
cd matchacalc-backend
source .venv/bin/activate
python scripts/load_market_data.py ../market_data_Q4_2025.json
```

## Если нужно применить миграции

```bash
cd matchacalc-backend
source .venv/bin/activate
alembic upgrade head
python scripts/seed_db.py
```
