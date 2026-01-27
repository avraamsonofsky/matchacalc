"""
Базовые тесты API
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """Тест корневого эндпоинта"""
    response = client.get("/")
    assert response.status_code == 200
    assert "MatchaCalc" in response.json()["message"]


def test_health():
    """Тест health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_get_reports():
    """Тест получения списка отчётов"""
    response = client.get("/api/v1/reports")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_location_groups():
    """Тест получения групп локаций"""
    response = client.get("/api/v1/reports/location-groups")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_scenarios():
    """Тест получения сценариев"""
    response = client.get("/api/v1/reports/scenarios")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    # Проверяем, что есть базовые сценарии
    scenarios = response.json()
    scenario_ids = [s["id"] for s in scenarios]
    assert "base" in scenario_ids
    assert "pes" in scenario_ids
    assert "opt" in scenario_ids
