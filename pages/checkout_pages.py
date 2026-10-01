"""Три шага оформления заказа: данные покупателя → проверка заказа → подтверждение."""

from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage


class CheckoutInfoPage(BasePage):
    path = "/checkout-step-one.html"
    title = "Checkout: Your Information"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.first_name = page.get_by_test_id("firstName")
        self.last_name = page.get_by_test_id("lastName")
        self.postal_code = page.get_by_test_id("postalCode")
        self.continue_button = page.get_by_test_id("continue")
        self.cancel_button = page.get_by_test_id("cancel")
        self.error = page.get_by_test_id("error")

    def fill(self, first_name: str, last_name: str, postal_code: str) -> None:
        self.first_name.fill(first_name)
        self.last_name.fill(last_name)
        self.postal_code.fill(postal_code)

    def submit(self, first_name: str, last_name: str, postal_code: str) -> CheckoutOverviewPage:
        self.fill(first_name, last_name, postal_code)
        self.continue_button.click()
        return CheckoutOverviewPage(self.page)


class CheckoutOverviewPage(BasePage):
    path = "/checkout-step-two.html"
    title = "Checkout: Overview"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.item_names = page.get_by_test_id("inventory-item-name")
        self.subtotal = page.get_by_test_id("subtotal-label")
        self.tax = page.get_by_test_id("tax-label")
        self.total = page.get_by_test_id("total-label")
        self.finish_button = page.get_by_test_id("finish")
        self.cancel_button = page.get_by_test_id("cancel")

    def finish(self) -> CheckoutCompletePage:
        self.finish_button.click()
        return CheckoutCompletePage(self.page)


class CheckoutCompletePage(BasePage):
    path = "/checkout-complete.html"
    title = "Checkout: Complete!"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.complete_header = page.get_by_test_id("complete-header")
        self.back_home_button = page.get_by_test_id("back-to-products")
