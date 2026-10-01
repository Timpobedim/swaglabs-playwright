"""Корзина: счётчик в шапке, состав, хранение между перезагрузками и сброс состояния."""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from helpers.data import product
from helpers.money import format_money
from pages.cart_page import CartPage
from pages.inventory_page import InventoryPage

BACKPACK = product("sauce-labs-backpack")
BIKE_LIGHT = product("sauce-labs-bike-light")


@pytest.mark.smoke
def test_add_and_remove_update_cart_badge(inventory: InventoryPage) -> None:
    inventory.add_to_cart(BACKPACK)
    inventory.add_to_cart(BIKE_LIGHT)
    inventory.header.expect_cart_count(2)

    inventory.remove_from_cart(BACKPACK)

    inventory.header.expect_cart_count(1)


def test_cart_lists_added_products(inventory: InventoryPage) -> None:
    inventory.add_to_cart(BACKPACK)
    inventory.add_to_cart(BIKE_LIGHT)

    cart = inventory.open_cart().should_be_opened()

    expect(cart.item_names).to_have_text([BACKPACK.name, BIKE_LIGHT.name])
    expect(cart.item_prices).to_have_text([format_money(BACKPACK.price), format_money(BIKE_LIGHT.price)])
    expect(cart.quantities).to_have_text(["1", "1"])


def test_remove_product_in_cart(inventory: InventoryPage) -> None:
    inventory.add_to_cart(BACKPACK)
    inventory.add_to_cart(BIKE_LIGHT)
    cart = inventory.open_cart()

    cart.remove(BACKPACK)

    expect(cart.item_names).to_have_text([BIKE_LIGHT.name])
    cart.header.expect_cart_count(1)


def test_cart_survives_page_reload(inventory: InventoryPage) -> None:
    inventory.add_to_cart(BACKPACK)

    inventory.page.reload()

    inventory.header.expect_cart_count(1)
    expect(inventory.open_cart().item_names).to_have_text([BACKPACK.name])


def test_reset_app_state_empties_cart(inventory: InventoryPage) -> None:
    inventory.add_to_cart(BACKPACK)
    inventory.add_to_cart(BIKE_LIGHT)

    inventory.header.reset_app_state()

    inventory.header.expect_cart_count(0)
    cart = CartPage(inventory.page).open().should_be_opened()
    expect(cart.items).to_have_count(0)
