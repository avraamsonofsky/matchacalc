#!/bin/bash
# Скрипт для запуска фронтенда

cd "$(dirname "$0")/matchacalc-frontend"
python3 -m http.server 8080
