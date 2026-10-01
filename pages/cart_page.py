from __future__ import annotations

from playwright.sync_api import Page

from helpers.data import Product
from pages.base_page import BasePage
from pages.checkout_pages import CheckoutInfoPage


class CartPage(BasePage):
    path = "/cart.html"
    title = "Your Cart"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.items = page.get_by_test_id("inventory-item")
        self.item_names = page.get_by_test_id("inventory-item-name")
        self.item_prices = page.get_by_test_id("inventory-item-price")
        self.quantities = page.get_by_test_id("item-quantity")
        self.checkout_button = page.get_by_test_id("checkout")
        self.continue_shopping_button = page.get_by_test_id("continue-shopping")

    def remove(self, product: Product) -> None:
        self.page.get_by_test_id(f"remove-{product.slug}").click()

    def checkout(self) -> CheckoutInfoPage:
        self.checkout_button.click()
        return CheckoutInfoPage(self.page)
