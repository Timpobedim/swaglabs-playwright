"""Сессия покупателя: повторное использование авторизации и выход."""

from __future__ import annotations

from playwright.sync_api import Page

from helpers.users import STANDARD_USER
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


def test_customer_starts_already_logged_in(page: Page) -> None:
    InventoryPage(page).open().should_be_opened()

    cookies = {cookie["name"]: cookie["value"] for cookie in page.context.cookies()}
    assert cookies.get("session-username") == STANDARD_USER


def test_logout_ends_session(inventory: InventoryPage) -> None:
    inventory.header.logout()
    login_page = LoginPage(inventory.page).should_be_opened()

    inventory.page.goto(InventoryPage.path)

    login_page.expect_error("Epic sadface: You can only access '/inventory.html' when you are logged in.")
