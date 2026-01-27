"""
Тесты фронтенда с Playwright
"""
import pytest
from playwright.sync_api import Page, expect


def test_homepage_loads(page: Page):
    """Проверка загрузки главной страницы"""
    page.goto("http://localhost:8080")
    expect(page).to_have_title("MatchaCalc - Калькулятор доходности недвижимости")
    expect(page.locator(".hero-modern")).to_be_visible()


def test_dropdowns_populated(page: Page):
    """Проверка загрузки выпадающих списков"""
    page.goto("http://localhost:8080")
    
    # Ждём загрузки данных
    page.wait_for_timeout(2000)
    
    # Проверяем список районов
    location_select = page.locator("#location-group")
    expect(location_select).to_be_visible()
    options = location_select.locator("option")
    expect(options).to_have_count(6, timeout=5000)  # 5 районов + placeholder
    
    # Проверяем список сценариев
    scenario_select = page.locator("#scenario")
    expect(scenario_select).to_be_visible()
    scenario_options = scenario_select.locator("option")
    expect(scenario_options).to_have_count(4, timeout=5000)  # 3 сценария + placeholder
    
    # Проверяем список отчётов
    report_select = page.locator("#report")
    expect(report_select).to_be_visible()
    report_options = report_select.locator("option")
    expect(report_options).to_have_count(4, timeout=5000)  # 3 отчёта + placeholder


def test_calculator_form_submission(page: Page):
    """Проверка отправки формы калькулятора"""
    page.goto("http://localhost:8080")
    page.wait_for_timeout(2000)
    
    # Заполняем форму
    page.fill("#purchase-price", "50000000")
    page.fill("#area", "150")
    page.select_option("#location-group", "moscow_city")
    page.select_option("#scenario", "base")
    page.select_option("#report", index=1)  # Первый отчёт
    
    # Устанавливаем дату
    page.select_option("#rve-year", "2026")
    page.select_option("#rve-month", "06")
    
    # Устанавливаем срок владения
    page.fill("#holding-years", "7")
    
    # Отправляем форму
    calculate_btn = page.locator("#calculate-btn")
    expect(calculate_btn).to_be_visible()
    calculate_btn.click()
    
    # Ждём результатов
    page.wait_for_timeout(3000)
    
    # Проверяем, что результаты отображаются
    results = page.locator("#results")
    expect(results).to_be_visible(timeout=10000)
    
    # Проверяем наличие метрик
    expect(page.locator("#rent-income")).to_be_visible()
    expect(page.locator("#npv")).to_be_visible()


def test_navigation_links(page: Page):
    """Проверка навигационных ссылок"""
    page.goto("http://localhost:8080")
    
    # Проверяем наличие навигации
    expect(page.locator(".navbar")).to_be_visible()
    expect(page.locator("#nav-login")).to_be_visible()
    expect(page.locator("#nav-register")).to_be_visible()


def test_responsive_design(page: Page):
    """Проверка адаптивности дизайна"""
    # Мобильный вид
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto("http://localhost:8080")
    
    expect(page.locator(".hero-modern")).to_be_visible()
    
    # Планшетный вид
    page.set_viewport_size({"width": 768, "height": 1024})
    page.reload()
    expect(page.locator(".calculator-layout")).to_be_visible()
    
    # Десктопный вид
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.reload()
    expect(page.locator(".calculator-layout")).to_be_visible()
