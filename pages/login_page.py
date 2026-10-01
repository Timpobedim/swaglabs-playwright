from __future__ import annotations

from typing import Self

from playwright.sync_api import Page, expect

from pages.inventory_page import InventoryPage


class LoginPage:
    path = "/"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.username = page.get_by_test_id("username")
        self.password = page.get_by_test_id("password")
        self.login_button = page.get_by_test_id("login-button")
        self.error = page.get_by_test_id("error")
        self.error_close = page.get_by_test_id("error-button")

    def open(self) -> Self:
        self.page.goto(self.path)
        return self

    def should_be_opened(self) -> Self:
        expect(self.login_button).to_be_visible()
        return self

    def submit(self, username: str, password: str) -> None:
        self.username.fill(username)
        self.password.fill(password)
        self.login_button.click()

    def login(self, username: str, password: str) -> InventoryPage:
        self.submit(username, password)
        return InventoryPage(self.page)

    def expect_error(self, text: str) -> None:
        expect(self.error).to_have_text(text)
