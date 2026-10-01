# Swag Labs UI Tests — автотесты интернет-магазина на Playwright

UI-автотесты демонстрационного интернет-магазина [Swag Labs](https://www.saucedemo.com):
вход, каталог, корзина, оформление заказа. Позитивные и негативные сценарии входа и обязательные
поля проверяются на данных из CSV и JSON, авторизация выполняется один раз на сессию через
storage state. Найденные дефекты оформлены баг-репортами и закреплены тестами-«сторожами».

**Стек:** Python 3.12 · Playwright · pytest · pytest-playwright · pytest-xdist · pytest-html ·
ruff · mypy (strict) · GitHub Actions.

## Найденные дефекты

Магазин специально содержит ошибки для «особых» пользователей — задача в том, чтобы найти их
исследованием, воспроизвести и оформить. Тест каждого дефекта проверяет **ожидаемое** поведение
и помечен `@pytest.mark.known_defect("SL-…")`: хук в `conftest.py` превращает пометку в
`xfail(strict=True, raises=AssertionError)`. Пока дефект есть, прогон зелёный. Когда его исправят,
тест станет XPASS и прогон покраснеет. Ошибка окружения (упавший сайт, сломанный локатор)
под дефект не маскируется — это обычное падение.

| ID | Пользователь | Дефект | Серьёзность |
|---|---|---|---|
| [SL-001](docs/bug-reports/SL-001.md) | standard_user | `Item total: $121.94999999999999` — сумма без округления до центов | Minor |
| [SL-002](docs/bug-reports/SL-002.md) | problem_user | ввод фамилии затирает имя, заказ не оформить | Critical |
| [SL-003](docs/bug-reports/SL-003.md) | problem_user | у всех товаров одна картинка-заглушка | Major |
| [SL-004](docs/bug-reports/SL-004.md) | problem_user | сортировка не меняет порядок товаров | Major |
| [SL-005](docs/bug-reports/SL-005.md) | error_user | кнопка Finish не завершает заказ | Critical |
| [SL-006](docs/bug-reports/SL-006.md) | visual_user | цены в каталоге не совпадают с реальными | Major |
| [SL-007](docs/bug-reports/SL-007.md) | performance_glitch_user | вход занимает около 5 с при бюджете 2 с | Major |

SL-001 — пример того, зачем нужна исследовательская сессия: дефект проявляется только на
определённом наборе и порядке товаров, а первая версия автотеста на полном каталоге дала XPASS.
После этого состав корзины был восстановлен точно — история в баг-репорте.

## Запуск

```bash
uv sync --group dev
uv run playwright install chromium
uv run pytest                  # все тесты, отчёт — reports/report.html
uv run pytest -n 4             # параллельно, у каждого процесса своя авторизация
uv run pytest -m smoke         # только ключевые сценарии
uv run pytest --headed --slowmo 300 tests/customer/test_checkout.py   # посмотреть глазами
uv run pytest --base-url https://staging.example.com                  # другой стенд
```

Упавший тест оставляет скриншот и трейс Playwright в `test-results/`. Трейс открывается командой
`uv run playwright show-trace test-results/<тест>/trace.zip`.

## Структура

```
pages/            # Page Object: вход, каталог, карточка, корзина, оформление, шапка
helpers/          # данные (CSV/JSON), деньги в Decimal, учётные записи, таймауты
data/             # эталонный каталог, пользователи, негативные логины, обязательные поля
tests/
├── guest/        # без авторизации: вход, закрытые страницы, дефекты «особых» пользователей
└── customer/     # standard_user через storage state: сессия, каталог, корзина, оформление
docs/bug-reports/ # SL-001 … SL-007
conftest.py       # атрибут data-test, авторизация на сессию, known_defect → xfail(strict)
```

## Результат прогона

51 тест: 44 проходят, 7 — ожидаемые падения известных дефектов; около 26 секунд в 4 потока.
ruff и mypy (strict) — без замечаний. Проверено 11.09.2026 на Windows 10, Chromium 151 (Playwright 1.62).
