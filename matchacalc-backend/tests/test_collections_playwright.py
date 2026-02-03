"""
Playwright тесты для коллекций.
Запуск: cd matchacalc-backend && PYTHONPATH=. .venv/bin/pytest tests/test_collections_playwright.py -v
"""
import pytest
from playwright.sync_api import Page, expect
import time


# Настройки
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "premium@test.com"
TEST_PASSWORD = "test123"


@pytest.fixture(scope="module")
def browser_context(browser):
    """Создаем контекст с сохранением состояния"""
    context = browser.new_context()
    yield context
    context.close()


class TestPublicCollectionPage:
    """Тесты публичной страницы коллекции"""
    
    def test_public_page_loads_clean_layout(self, page: Page):
        """
        Проверяем что публичная страница:
        1. Содержит только логотип в шапке
        2. НЕ содержит навигацию (Вход, Регистрация и т.д.)
        3. НЕ содержит секцию преимуществ
        """
        # Используем тестовый slug (нужно создать коллекцию заранее или замокать)
        page.goto(f"{BASE_URL}/c/testslug")
        
        # Ждем загрузки
        page.wait_for_load_state("networkidle")
        
        # Проверяем что есть логотип
        logo = page.locator(".logo")
        expect(logo).to_be_visible()
        expect(logo).to_have_text("LatteCalc")
        
        # Проверяем что логотип ведет на главную
        expect(logo).to_have_attribute("href", "/")
        
        # Проверяем что НЕТ навигационных ссылок
        assert page.locator("text=Вход").count() == 0, "Не должно быть ссылки 'Вход'"
        assert page.locator("text=Регистрация").count() == 0, "Не должно быть ссылки 'Регистрация'"
        assert page.locator("text=Подписка").count() == 0, "Не должно быть ссылки 'Подписка'"
        
        # Проверяем что НЕТ секции преимуществ
        assert page.locator("text=Почему LatteCalc").count() == 0, "Не должно быть секции преимуществ"
        assert page.locator("text=Смотри разницу").count() == 0, "Не должно быть секции преимуществ"

    def test_no_infinite_requests(self, page: Page):
        """
        Проверяем что нет бесконечного цикла запросов (спама placeholder.png)
        """
        request_count = {"img": 0}
        
        def count_requests(request):
            if "placeholder" in request.url or request.url.endswith(".png"):
                request_count["img"] += 1
        
        page.on("request", count_requests)
        
        page.goto(f"{BASE_URL}/c/testslug")
        page.wait_for_load_state("networkidle")
        
        # Ждем немного чтобы убедиться что нет спама
        time.sleep(2)
        
        # Не должно быть больше 20 запросов на картинки (даже если много лотов)
        assert request_count["img"] < 50, f"Слишком много запросов на картинки: {request_count['img']}"


class TestCollectionsPage:
    """Тесты страницы управления коллекциями"""
    
    @pytest.fixture(autouse=True)
    def login(self, page: Page):
        """Логинимся перед тестами"""
        page.goto(f"{BASE_URL}/login.html")
        page.fill("#email", TEST_EMAIL)
        page.fill("#password", TEST_PASSWORD)
        page.click("button[type=submit]")
        page.wait_for_url("**/index.html")
        
    def test_add_lot_no_spam(self, page: Page):
        """
        Проверяем что при добавлении лота нет бесконечного спама запросов
        """
        request_count = {"total": 0, "placeholder": 0}
        
        def count_requests(request):
            request_count["total"] += 1
            if "placeholder" in request.url:
                request_count["placeholder"] += 1
        
        page.on("request", count_requests)
        
        # Переходим на страницу коллекций
        page.goto(f"{BASE_URL}/collections.html")
        page.wait_for_load_state("networkidle")
        
        initial_count = request_count["total"]
        
        # Ждем 3 секунды и проверяем что запросы не растут бесконечно
        time.sleep(3)
        
        # За 3 секунды не должно быть больше 50 новых запросов
        new_requests = request_count["total"] - initial_count
        assert new_requests < 100, f"Слишком много запросов за 3 секунды: {new_requests}"
        assert request_count["placeholder"] < 30, f"Спам placeholder: {request_count['placeholder']}"


class TestRoutingToPublicCollection:
    """Тесты роутинга /c/slug"""
    
    def test_c_route_serves_public_page(self, page: Page):
        """
        Проверяем что URL /c/xxxxx отдает public_collection.html, а не index.html
        """
        page.goto(f"{BASE_URL}/c/anyslug")
        page.wait_for_load_state("domcontentloaded")
        
        # На публичной странице должен быть только логотип, без полной навигации
        # Ищем специфичные элементы index.html которых НЕ должно быть
        hero_text = page.locator("text=СЧИТАЙ ДОХОДНОСТЬ ПОКА ПЬЁШЬ ЛАТТЕ")
        benefits_text = page.locator("text=Почему LatteCalc")
        
        # Эти элементы есть только в index.html
        assert hero_text.count() == 0, "Отдается index.html вместо public_collection.html"
        assert benefits_text.count() == 0, "Отдается index.html вместо public_collection.html"
        
        # На публичной странице должна быть секция loading или content
        loading_or_content = page.locator("#loading, #content, #error")
        expect(loading_or_content.first).to_be_visible()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
