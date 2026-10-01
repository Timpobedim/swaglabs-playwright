from __future__ import annotations

import re
from typing import ClassVar, Self

from playwright.sync_api import Page, expect

from pages.header import Header


class BasePage:
    """Страница магазина после входа: адрес, заголовок в шапке и общая шапка с корзиной и меню."""

    path: ClassVar[str]
    title: ClassVar[str]

    def __init__(self, page: Page) -> None:
        self.page = page
        self.header = Header(page)
        self.heading = page.get_by_test_id("title")

    def open(self) -> Self:
        self.page.goto(self.path)
        return self

    def should_be_opened(self) -> Self:
        expect(self.page).to_have_url(re.compile(f"{re.escape(self.path)}$"))
        expect(self.heading).to_have_text(self.title)
        return self
