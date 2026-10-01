"""Вход в магазин: позитивные и негативные сценарии, данные — из data/*.json и data/*.csv."""

from __future__ import annotations

import re
import time

import pytest
from playwright.sync_api import Page, expect

from helpers.data import catalog, load_csv, load_json
from helpers.timeouts import LOGIN_BUDGET_SECONDS, SLOW_LOGIN_TIMEOUT_MS
from helpers.users import PASSWORD, STANDARD_USER
from pages.login_page import LoginPage

INVALID_LOGINS: list[dict[str, str]] = load_json("invalid_logins.json")
ACCEPTED_USERS = load_csv("users.csv")


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    return LoginPage(page).open().should_be_opened()


@pytest.mark.smoke
def test_standard_user_logs_in(login_page: LoginPage) -> None:
    inventory = login_page.login(STANDARD_USER, PASSWORD).should_be_opened()

    expect(inventory.items).to_have_count(len(catalog()))
    inventory.header.expect_cart_count(0)


@pytest.mark.parametrize("case", INVALID_LOGINS, ids=[case["id"] for case in INVALID_LOGINS])
def test_invalid_login_is_rejected(login_page: LoginPage, case: dict[str, str]) -> None:
    login_page.submit(case["username"], case["password"])

    login_page.expect_error(case["error"])
    expect(login_page.page).to_have_url(re.compile(r"/$"))


def test_error_message_can_be_closed(login_page: LoginPage) -> None:
    login_page.submit("", "")

    login_page.error_close.click()

    expect(login_page.error).to_be_hidden()


@pytest.mark.parametrize("user", ACCEPTED_USERS, ids=[user["username"] for user in ACCEPTED_USERS])
def test_accepted_users_reach_catalog(login_page: LoginPage, user: dict[str, str]) -> None:
    inventory = login_page.login(user["username"], PASSWORD)

    # Здесь проверяется сам факт входа; скорость входа — в отдельных тестах с бюджетом времени.
    expect(inventory.heading).to_have_text("Products", timeout=SLOW_LOGIN_TIMEOUT_MS)


def test_standard_user_logs_in_within_budget(login_page: LoginPage) -> None:
    started = time.monotonic()

    login_page.login(STANDARD_USER, PASSWORD).should_be_opened()

    elapsed = time.monotonic() - started
    assert elapsed < LOGIN_BUDGET_SECONDS, f"вход занял {elapsed:.1f} с при бюджете {LOGIN_BUDGET_SECONDS} с"
