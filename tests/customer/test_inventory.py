"""Каталог: состав, цены, сортировка и карточка товара."""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import expect

from helpers.data import catalog, product
from helpers.money import format_money
from pages.inventory_page import InventoryPage


@pytest.mark.smoke
def test_catalog_matches_reference_data(inventory: InventoryPage) -> None:
    expect(inventory.item_names).to_have_text([item.name for item in catalog()])
    expect(inventory.item_prices).to_have_text([format_money(item.price) for item in catalog()])


@pytest.mark.parametrize(("option", "reverse"), [("az", False), ("za", True)], ids=["name-a-z", "name-z-a"])
def test_sort_by_name(inventory: InventoryPage, option: str, reverse: bool) -> None:
    inventory.sort_by(option)

    expect(inventory.item_names).to_have_text(sorted((item.name for item in catalog()), reverse=reverse))


@pytest.mark.parametrize(
    ("option", "reverse"), [("lohi", False), ("hilo", True)], ids=["price-low-high", "price-high-low"]
)
def test_sort_by_price(inventory: InventoryPage, option: str, reverse: bool) -> None:
    inventory.sort_by(option)

    # У двух футболок одинаковая цена, поэтому сравниваются цены, а не названия.
    expected = [format_money(price) for price in sorted((item.price for item in catalog()), reverse=reverse)]
    expect(inventory.item_prices).to_have_text(expected)


def test_product_card_matches_catalog(inventory: InventoryPage) -> None:
    backpack = product("sauce-labs-backpack")

    card = inventory.open_product(backpack).should_be_opened()

    expect(card.page).to_have_url(re.compile(rf"id={backpack.id}$"))
    expect(card.name).to_have_text(backpack.name)
    expect(card.price).to_have_text(format_money(backpack.price))
    card.add_button.click()
    expect(card.remove_button).to_be_visible()
    card.header.expect_cart_count(1)
    card.back_button.click()
    InventoryPage(card.page).should_be_opened()
