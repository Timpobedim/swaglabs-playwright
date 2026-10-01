"""Тесты покупателя стартуют уже авторизованными: storage_state подставляется в контекст браузера."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import Page

from pages.inventory_page import InventoryPage


@pytest.fixture(scope="session")
def browser_context_args(
    browser_context_args: dict[str, Any], customer_storage_state: Path
) -> dict[str, Any]:
    return {**browser_context_args, "storage_state": customer_storage_state}


@pytest.fixture
def inventory(page: Page) -> InventoryPage:
    return InventoryPage(page).open().should_be_opened()
