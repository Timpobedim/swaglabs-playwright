from __future__ import annotations

import re
from typing import Self

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class ItemPage(BasePage):
    """Карточка товара. Заголовка в шапке нет — вместо него кнопка «Back to products»."""

    path = "/inventory-item.html"
    title = ""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.name = page.get_by_test_id("inventory-item-name")
        self.description = page.get_by_test_id("inventory-item-desc")
        self.price = page.get_by_test_id("inventory-item-price")
        self.add_button = page.get_by_test_id("add-to-cart")
        self.remove_button = page.get_by_test_id("remove")
        self.back_button = page.get_by_test_id("back-to-products")

    def should_be_opened(self) -> Self:
        expect(self.page).to_have_url(re.compile(r"/inventory-item\.html\?id=\d+$"))
        expect(self.back_button).to_be_visible()
        return self
