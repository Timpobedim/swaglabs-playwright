"""Дефекты, найденные при исследовании магазина под «особыми» пользователями.

Каждый тест проверяет ОЖИДАЕМОЕ поведение и помечен known_defect → xfail(strict=True):
пока дефект есть, прогон зелёный; когда его исправят, тест станет XPASS и прогон подсветит,
что пора снять пометку. Описание, шаги и фактический результат — в docs/bug-reports/.
"""

from __future__ import annotations

import time
from collections.abc import Callable

import pytest
from playwright.sync_api import Page, expect

from helpers.data import catalog, product
from helpers.money import format_money
from helpers.timeouts import DEFECT_TIMEOUT_MS, LOGIN_BUDGET_SECONDS, SLOW_LOGIN_TIMEOUT_MS
from helpers.users import ERROR_USER, PASSWORD, PERFORMANCE_GLITCH_USER, PROBLEM_USER, VISUAL_USER
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage

BACKPACK = product("sauce-labs-backpack")

LoginAs = Callable[[str], InventoryPage]


@pytest.fixture
def login_as(page: Page) -> LoginAs:
    def _login(username: str) -> InventoryPage:
        inventory = LoginPage(page).open().login(username, PASSWORD)
        expect(inventory.heading).to_have_text("Products", timeout=SLOW_LOGIN_TIMEOUT_MS)
        return inventory

    return _login


@pytest.mark.known_defect("SL-002", "problem_user: ввод фамилии затирает имя, оформить заказ нельзя")
def test_problem_user_can_fill_checkout_form(login_as: LoginAs) -> None:
    inventory = login_as(PROBLEM_USER)
    inventory.add_to_cart(BACKPACK)
    info = inventory.open_cart().checkout()

    info.fill("Анна", "Петрова", "101000")

    expect(info.first_name).to_have_value("Анна", timeout=DEFECT_TIMEOUT_MS)
    expect(info.last_name).to_have_value("Петрова", timeout=DEFECT_TIMEOUT_MS)


@pytest.mark.known_defect("SL-003", "problem_user: у всех товаров одна и та же картинка-заглушка")
def test_problem_user_sees_product_photos(login_as: LoginAs) -> None:
    inventory = login_as(PROBLEM_USER)

    sources = inventory.item_images.evaluate_all("images => images.map(image => image.getAttribute('src'))")

    assert len(set(sources)) == len(catalog()), f"уникальных картинок {len(set(sources))} из {len(catalog())}"


@pytest.mark.known_defect("SL-004", "problem_user: сортировка по цене не меняет порядок товаров")
def test_problem_user_can_sort_by_price(login_as: LoginAs) -> None:
    inventory = login_as(PROBLEM_USER)

    inventory.sort_by("lohi")

    expected = [format_money(price) for price in sorted(item.price for item in catalog())]
    expect(inventory.item_prices).to_have_text(expected, timeout=DEFECT_TIMEOUT_MS)


@pytest.mark.known_defect("SL-005", "error_user: кнопка Finish не завершает заказ")
def test_error_user_can_finish_order(login_as: LoginAs) -> None:
    inventory = login_as(ERROR_USER)
    inventory.add_to_cart(BACKPACK)
    overview = inventory.open_cart().checkout().submit("Анна", "Петрова", "101000")

    complete = overview.finish()

    expect(complete.complete_header).to_have_text("Thank you for your order!", timeout=DEFECT_TIMEOUT_MS)


@pytest.mark.known_defect("SL-006", "visual_user: цены в каталоге не совпадают с реальными")
def test_visual_user_sees_catalog_prices(login_as: LoginAs) -> None:
    inventory = login_as(VISUAL_USER)

    expected = [format_money(item.price) for item in catalog()]
    expect(inventory.item_prices).to_have_text(expected, timeout=DEFECT_TIMEOUT_MS)


@pytest.mark.known_defect("SL-007", "performance_glitch_user: вход занимает около 5 секунд")
def test_performance_glitch_user_logs_in_within_budget(page: Page) -> None:
    login_page = LoginPage(page).open()
    started = time.monotonic()

    inventory = login_page.login(PERFORMANCE_GLITCH_USER, PASSWORD)
    expect(inventory.heading).to_have_text("Products", timeout=SLOW_LOGIN_TIMEOUT_MS)

    elapsed = time.monotonic() - started
    assert elapsed < LOGIN_BUDGET_SECONDS, f"вход занял {elapsed:.1f} с при бюджете {LOGIN_BUDGET_SECONDS} с"
