"""Оформление заказа: обязательные поля, расчёт суммы и налога, завершение и отмена."""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal

import pytest
from playwright.sync_api import expect

from helpers.data import Product, catalog, load_json, product
from helpers.money import format_money, tax_for
from helpers.timeouts import DEFECT_TIMEOUT_MS
from pages.checkout_pages import CheckoutInfoPage, CheckoutOverviewPage
from pages.inventory_page import InventoryPage

REQUIRED_FIELDS: list[dict[str, str]] = load_json("checkout_required_fields.json")
BACKPACK = product("sauce-labs-backpack")
BIKE_LIGHT = product("sauce-labs-bike-light")
CUSTOMER = ("Анна", "Петрова", "101000")

# Корзина, на которой проявляется SL-001. Порядок важен: магазин складывает цены числами
# с плавающей точкой в порядке добавления, и именно эта последовательность даёт 121.94999999999999.
FLOAT_PRONE_CART = [
    product(slug)
    for slug in (
        "sauce-labs-bike-light",
        "sauce-labs-bolt-t-shirt",
        "test.allthethings()-t-shirt-(red)",
        "sauce-labs-backpack",
        "sauce-labs-fleece-jacket",
    )
]


@pytest.fixture
def checkout_info(inventory: InventoryPage) -> CheckoutInfoPage:
    inventory.add_to_cart(BACKPACK)
    return inventory.open_cart().checkout().should_be_opened()


def overview_for(inventory: InventoryPage, products: Sequence[Product]) -> CheckoutOverviewPage:
    for item in products:
        inventory.add_to_cart(item)
    return inventory.open_cart().checkout().submit(*CUSTOMER).should_be_opened()


def subtotal_of(products: Sequence[Product]) -> Decimal:
    return sum((item.price for item in products), Decimal(0))


@pytest.mark.parametrize("case", REQUIRED_FIELDS, ids=[case["id"] for case in REQUIRED_FIELDS])
def test_required_fields(checkout_info: CheckoutInfoPage, case: dict[str, str]) -> None:
    checkout_info.fill(case["first_name"], case["last_name"], case["postal_code"])

    checkout_info.continue_button.click()

    expect(checkout_info.error).to_have_text(case["error"])
    checkout_info.should_be_opened()


def test_order_totals_are_calculated(inventory: InventoryPage) -> None:
    inventory.add_to_cart(BACKPACK)
    inventory.add_to_cart(BIKE_LIGHT)

    overview = inventory.open_cart().checkout().submit(*CUSTOMER).should_be_opened()

    subtotal = BACKPACK.price + BIKE_LIGHT.price
    tax = tax_for(subtotal)
    expect(overview.item_names).to_have_text([BACKPACK.name, BIKE_LIGHT.name])
    expect(overview.subtotal).to_have_text(f"Item total: {format_money(subtotal)}")
    expect(overview.tax).to_have_text(f"Tax: {format_money(tax)}")
    expect(overview.total).to_have_text(f"Total: {format_money(subtotal + tax)}")


@pytest.mark.smoke
def test_completed_order_empties_cart(checkout_info: CheckoutInfoPage) -> None:
    complete = checkout_info.submit(*CUSTOMER).finish().should_be_opened()

    expect(complete.complete_header).to_have_text("Thank you for your order!")
    complete.header.expect_cart_count(0)
    complete.back_home_button.click()
    InventoryPage(complete.page).should_be_opened()


def test_cancel_on_overview_keeps_cart(checkout_info: CheckoutInfoPage) -> None:
    overview = checkout_info.submit(*CUSTOMER)

    overview.cancel_button.click()

    InventoryPage(overview.page).should_be_opened()
    overview.header.expect_cart_count(1)


def test_totals_for_whole_catalog(inventory: InventoryPage) -> None:
    overview = overview_for(inventory, catalog())

    subtotal = subtotal_of(catalog())
    tax = tax_for(subtotal)
    expect(overview.subtotal).to_have_text(f"Item total: {format_money(subtotal)}")
    expect(overview.tax).to_have_text(f"Tax: {format_money(tax)}")
    expect(overview.total).to_have_text(f"Total: {format_money(subtotal + tax)}")


def test_tax_and_total_are_correct_for_float_prone_cart(inventory: InventoryPage) -> None:
    """Налог и итог на корзине из SL-001 верные — дефект только в выводе суммы товаров."""
    overview = overview_for(inventory, FLOAT_PRONE_CART)

    subtotal = subtotal_of(FLOAT_PRONE_CART)
    tax = tax_for(subtotal)
    expect(overview.tax).to_have_text(f"Tax: {format_money(tax)}")
    expect(overview.total).to_have_text(f"Total: {format_money(subtotal + tax)}")


@pytest.mark.known_defect("SL-001", "сумма товаров выводится без округления до центов")
def test_subtotal_is_rounded_to_cents(inventory: InventoryPage) -> None:
    overview = overview_for(inventory, FLOAT_PRONE_CART)

    expected = f"Item total: {format_money(subtotal_of(FLOAT_PRONE_CART))}"
    expect(overview.subtotal).to_have_text(expected, timeout=DEFECT_TIMEOUT_MS)
