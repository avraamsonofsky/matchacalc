#!/bin/bash
# Скрипт для запуска бэкенда

cd "$(dirname "$0")/matchacalc-backend"
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
