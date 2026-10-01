from __future__ import annotations

from playwright.sync_api import Page, expect


class Header:
    """Шапка магазина: корзина и боковое меню. Есть на каждой странице после входа.

    Методы шапки не возвращают объекты страниц — так нет циклических импортов между страницами
    и не нужен импорт внутри функции.
    """

    def __init__(self, page: Page) -> None:
        self.page = page
        self.cart_link = page.get_by_test_id("shopping-cart-link")
        self.cart_badge = page.get_by_test_id("shopping-cart-badge")
        self._menu_button = page.get_by_role("button", name="Open Menu")
        self._logout_link = page.get_by_test_id("logout-sidebar-link")
        self._reset_link = page.get_by_test_id("reset-sidebar-link")

    def expect_cart_count(self, count: int) -> None:
        if count == 0:
            expect(self.cart_badge).to_be_hidden()
        else:
            expect(self.cart_badge).to_have_text(str(count))

    def open_menu(self) -> None:
        self._menu_button.click()

    def logout(self) -> None:
        self.open_menu()
        self._logout_link.click()

    def reset_app_state(self) -> None:
        self.open_menu()
        self._reset_link.click()
