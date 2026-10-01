"""Страницы магазина недоступны без входа: прямой переход возвращает на форму входа с объяснением."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from pages.login_page import LoginPage

PROTECTED_PAGES = [
    "/inventory.html",
    "/inventory-item.html?id=4",
    "/cart.html",
    "/checkout-step-one.html",
    "/checkout-step-two.html",
    "/checkout-complete.html",
]


@pytest.mark.parametrize("path", PROTECTED_PAGES)
def test_protected_page_requires_login(page: Page, path: str) -> None:
    page.goto(path)

    login_page = LoginPage(page).should_be_opened()
    page_name = path.split("?")[0]
    login_page.expect_error(f"Epic sadface: You can only access '{page_name}' when you are logged in.")
