#!/bin/bash
echo "Проверка API эндпоинтов..."
echo ""
echo "1. Проверка районов:"
curl -s http://localhost:8000/api/v1/reports/location-groups | python3 -m json.tool | head -20
echo ""
echo "2. Проверка сценариев:"
curl -s http://localhost:8000/api/v1/reports/scenarios | python3 -m json.tool | head -20
echo ""
echo "3. Проверка отчётов:"
curl -s http://localhost:8000/api/v1/reports | python3 -m json.tool | head -20
