"""Общие фикстуры: атрибут тестовых id, одна авторизация на сессию, пометка известных дефектов."""

from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import Browser, Playwright

from helpers.users import PASSWORD, STANDARD_USER
from pages.login_page import LoginPage


@pytest.fixture(scope="session", autouse=True)
def _data_test_attribute(playwright: Playwright) -> None:
    # В Swag Labs тестовые атрибуты называются data-test, а Playwright по умолчанию ищет data-testid.
    playwright.selectors.set_test_id_attribute("data-test")


@pytest.fixture(scope="session")
def customer_storage_state(browser: Browser, base_url: str, tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Вход через UI один раз на сессию (на каждый процесс xdist).

    Cookie и localStorage сохраняются в файл и подставляются в контекст каждого теста
    из tests/customer: тест получает чистый браузер, но уже авторизованный.
    """
    context = browser.new_context(base_url=base_url)
    try:
        page = context.new_page()
        LoginPage(page).open().login(STANDARD_USER, PASSWORD).should_be_opened()
        path = tmp_path_factory.mktemp("auth") / f"{STANDARD_USER}.json"
        context.storage_state(path=path)
    finally:
        context.close()
    return path


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """known_defect("SL-001", "…") превращается в xfail(strict=True) со ссылкой на баг-репорт.

    Пока дефект есть, тест «ожидаемо падает». Когда дефект исправят, тест станет XPASS,
    и прогон покраснеет — сигнал снять пометку и закрыть баг-репорт.
    raises=AssertionError: ожидаемым считается только провал проверки. Ошибка окружения
    (сайт недоступен, сломанный локатор) остаётся обычным падением и не маскируется под дефект.
    """
    for item in items:
        marker = item.get_closest_marker("known_defect")
        if marker is not None:
            bug_id, summary = marker.args
            reason = f"{bug_id}: {summary} (docs/bug-reports/{bug_id}.md)"
            item.add_marker(pytest.mark.xfail(reason=reason, strict=True, raises=AssertionError))
