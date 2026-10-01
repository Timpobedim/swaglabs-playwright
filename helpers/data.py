"""Тестовые данные из data/: пути строятся от корня проекта, а не от текущего каталога запуска."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from decimal import Decimal
from functools import cache
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_json(name: str) -> Any:
    with (DATA_DIR / name).open(encoding="utf-8") as fh:
        return json.load(fh)


def load_csv(name: str) -> list[dict[str, str]]:
    with (DATA_DIR / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


@dataclass(frozen=True)
class Product:
    id: int
    slug: str  # часть data-test кнопок: add-to-cart-<slug>, remove-<slug>
    name: str
    price: Decimal


@cache
def catalog() -> tuple[Product, ...]:
    """Эталонный каталог в порядке «по названию A→Z» — так магазин показывает товары по умолчанию."""
    return tuple(
        Product(id=item["id"], slug=item["slug"], name=item["name"], price=Decimal(item["price"]))
        for item in load_json("catalog.json")
    )


def product(slug: str) -> Product:
    for item in catalog():
        if item.slug == slug:
            return item
    raise KeyError(f"товара {slug!r} нет в data/catalog.json")
