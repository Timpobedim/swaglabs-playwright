"""Деньги считаем в Decimal: сравнение сумм через float само по себе источник ложных падений."""

from __future__ import annotations

import re
from decimal import ROUND_HALF_UP, Decimal

# Ставка выведена из наблюдений: $39.98 → налог $3.20, $121.95 → $9.76.
TAX_RATE = Decimal("0.08")
CENT = Decimal("0.01")

_AMOUNT = re.compile(r"\$(\d+(?:\.\d+)?)")


def parse_money(text: str) -> Decimal:
    match = _AMOUNT.search(text)
    if match is None:
        raise ValueError(f"в строке нет суммы в долларах: {text!r}")
    return Decimal(match.group(1))


def format_money(amount: Decimal) -> str:
    return f"${amount.quantize(CENT)}"


def tax_for(subtotal: Decimal) -> Decimal:
    return (subtotal * TAX_RATE).quantize(CENT, rounding=ROUND_HALF_UP)
