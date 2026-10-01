from __future__ import annotations

import re
from decimal import Decimal

from playwright.sync_api import Page, expect

from helpers.data import Product
from helpers.money import parse_money
from pages.base_page import BasePage
from pages.cart_page import CartPage
from pages.item_page import ItemPage


class InventoryPage(BasePage):
    path = "/inventory.html"
    title = "Products"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.items = page.get_by_test_id("inventory-item")
        self.item_names = page.get_by_test_id("inventory-item-name")
        self.item_prices = page.get_by_test_id("inventory-item-price")
        self.item_images = self.items.locator("img")
        self.sort_select = page.get_by_test_id("product-sort-container")

    def sort_by(self, option: str) -> None:
        """option — значение из списка сортировки: az, za, lohi, hilo."""
        self.sort_select.select_option(option)

    def add_to_cart(self, product: Product) -> None:
        self.page.get_by_test_id(f"add-to-cart-{product.slug}").click()

    def remove_from_cart(self, product: Product) -> None:
        self.page.get_by_test_id(f"remove-{product.slug}").click()

    def prices(self) -> list[Decimal]:
        expect(self.items).not_to_have_count(0)
        return [parse_money(text) for text in self.item_prices.all_inner_texts()]

    def open_product(self, product: Product) -> ItemPage:
        self.item_names.filter(has_text=re.compile(f"^{re.escape(product.name)}$")).click()
        return ItemPage(self.page)

    def open_cart(self) -> CartPage:
        self.header.cart_link.click()
        return CartPage(self.page)
