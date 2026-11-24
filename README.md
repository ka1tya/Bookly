# Bookly

Bookly — інтернет-магазин книг: клієнти переглядають каталог за категоріями, оформлюють замовлення з
кількома книгами та оплачують їх карткою або готівкою. Курсовий проєкт реалізує бізнес-сценарії
магазину поверх бази PostgreSQL.

Вимоги, бізнес-правила та сутності: [docs/requirements.md](docs/requirements.md).

## Команда

| Учасник          | Сутності            |
| ---------------- | ------------------- |
| Варенко Катерина | Customer, Address   |
| Поліщук Анна     | Category, Book      |
| Лобода Аліна     | Author, Orders      |
| Сітковська Аліна | Order_item, Payment |

Внесок кожної учасниці: [CONTRIBUTIONS.md](CONTRIBUTIONS.md).

## Стек

- **СУБД:** PostgreSQL 16
- **Мова:** Python 3.12
- **ORM:** SQLAlchemy 2.0 (драйвер psycopg 3)
- **Тести:** pytest, pytest-cov
- **Середовище:** Docker Compose (postgres, postgres_test, pgAdmin, app)

## Налаштування та запуск

Потрібні Git і запущений Docker Desktop.

1. Клонуйте репозиторій:

   ```bash
   git clone https://github.com/ka1tya/Bookly.git
   cd Bookly
   ```

2. (Необов'язково) Скопіюйте `.env.example` у `.env`, якщо потрібні інші паролі чи імена. Без `.env` працюють значення за замовчуванням.
3. Запустіть сервіси:

   ```bash
   docker compose up -d --build
   ```

| Сервіс          | Що це                                                     | Порт |
| --------------- | --------------------------------------------------------- | ---- |
| `postgres`      | робоча база `bookly`, дані в томі `postgres_data`         | 5432 |
| `postgres_test` | окрема тестова база `bookly_test`, дані в пам'яті (tmpfs) | 5433 |
| `pgadmin`       | веб-інтерфейс до бази                                     | 8080 |
| `app`           | застосунок Python                                         | —    |

- Обидві бази створюються з файлів `migrations/` за алфавітом: таблиці, індекси, демо-дані. Робоча база — лише на порожньому томі, тестова — при кожному старті контейнера.
- pgAdmin: <http://localhost:8080>, відкривається без входу.
  Сервер: Host `postgres`, Port `5432`, Database `bookly`, Username `bookly`, Password `bookly_password`.

Запустити застосунок (перевіряє підключення й показує кількість записів у кожній таблиці):

```bash
docker compose run --rm app
```

Скинути робочу базу до початкового стану (видаляє всі дані):

```bash
docker compose down -v
docker compose up -d --build
```

## Запуск тестів

Усі тести в контейнері:

```bash
docker compose run --rm app pytest
```

Лише юніт- або лише інтеграційні тести:

```bash
docker compose run --rm app pytest test/unit
```

```bash
docker compose run --rm app pytest test/integration
```

Локально (потрібен Python 3.12+ і запущена тестова база `docker compose up -d postgres_test`):

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest
```

- Тести працюють з окремою базою `bookly_test`, а не з робочою.
- Кожен інтеграційний тест виконується в транзакції, яку в кінці відкочено, тому тести не впливають один на одного.
- Звіт покриття (`--cov=src`) виводиться автоматично.

## Структура

```
Bookly/
├── docker-compose.yml       postgres, postgres_test, pgAdmin, app
├── Dockerfile               образ застосунку
├── .env.example             приклад змінних середовища
├── requirements.txt
├── pyproject.toml           налаштування pytest і покриття
├── docs/
│   ├── requirements.md      вимоги, бізнес-правила, сутності
│   ├── schema.md            опис таблиць, індексів, рішень
│   ├── queries.md           складні аналітичні запити
│   └── ER-diagram.png
├── migrations/
│   ├── 001_initial_schema.sql   таблиці
│   ├── 002_add_indexes.sql      індекси
│   └── 003_seed_test_data.sql   демо-дані
├── src/
│   ├── db.py                підключення (DATABASE_URL)
│   ├── main.py              запуск: перевірка бази
│   ├── models/              ORM-моделі 9 таблиць і спільні статуси
│   ├── repositories/        доступ до даних
│   └── services/            бізнес-сценарії з транзакціями
├── test/
│   ├── conftest.py          спільні фікстури
│   ├── unit/                тести без бази
│   └── integration/         тести з PostgreSQL
├── README.md
└── CONTRIBUTIONS.md
```

## Приклади використання

### Демо запитів

Демо виводять результати простих і складних запитів кожної учасниці на демо-даних:

```bash
docker compose run --rm app python -m src.demo_customer
docker compose run --rm app python -m src.demo_book
docker compose run --rm app python -m src.demo_payment
```

### Сценарії

Сценарії викликаються з Python. Інтерактивна консоль у контейнері:

```bash
docker compose run --rm app python
```

Приклади нижче змінюють робочу базу. Повернути початкові дані: `docker compose down -v` і `docker compose up -d --build`. Номери в коментарях наведено для щойно створеної бази.

| Учасниця | Сценарії |
| --- | --- |
| Варенко Катерина | `register_customer`, `change_order_address`, `delete_customer` (`src/services/customer_service.py`) |
| Поліщук Анна | `create_book_with_categories`, `change_book_price`, `delete_book_not_in_orders` (`src/services/book_service.py`) |
| Сітковська Аліна | `add_items_to_order`, `confirm_cash_payment`, `remove_order_item` (`src/services/payment_service.py`) |
| Лобода Аліна | `create_order`, `change_order_status`, `delete_cancelled_order` (`src/services/order_service.py`) |

Реєстрація клієнта, замовлення, зміна статусу й підтвердження оплати готівкою:

```python
from src.db import get_session
from src.services.customer_service import register_customer
from src.services.order_service import change_order_status, create_order
from src.services.payment_service import confirm_cash_payment

with get_session() as session:
    customer = register_customer(session, "Ірина", "Мельник", "iryna@gmail.com", "+380661234567",
                                 [{"country": "Україна", "city": "Львів", "street": "вул. Городоцька 5"}])
    order = create_order(session, customer.id, customer.addresses[0].id,
                         [{"book_id": 1, "quantity": 2}, {"book_id": 5, "quantity": 1}], "готівка")
    print(order.id, order.status, order.payment.amount)   # 6 нове 880.00

    for status in ["збирається", "відправлено", "отримано"]:
        change_order_status(session, order.id, status)

    payment = confirm_cash_payment(session, order.id)
    print(payment.status)   # оплачено
```

Книга з категоріями і зміна ціни:

```python
from src.db import get_session
from src.services.book_service import change_book_price, create_book_with_categories

with get_session() as session:
    book = create_book_with_categories(session, author_id=3, title="Зелена миля", published_year=1996,
                                       price=310, category_ids=[3, 6])
    print(book.id, book.title, [c.category_name for c in book.categories])   # 8 Зелена миля ['Жахи', 'Трилер']

    book = change_book_price(session, book.id, 330)
    print(book.price)   # 330
```

Помилки. Сценарії кидають винятки з `src/services/errors.py` і відкочують транзакцію:

```python
from src.db import get_session
from src.services.errors import AppError
from src.services.order_service import create_order

with get_session() as session:
    try:
        create_order(session, customer_id=1, address_id=3, items=[{"book_id": 1, "quantity": 1}],
                     payment_method="картка")
    except AppError as error:
        print(type(error).__name__, error)   # ConflictError Адреса належить іншому клієнту
```

### Запити

```python
from src.db import get_session
from src.repositories.order_repository import customer_orders, orders_audit, search_authors

with get_session() as session:
    print([a.last_name for a in search_authors(session, "кінг")])   # ['Кінг']
    for row in customer_orders(session, customer_id=1):
        print(row.id, row.date, row.status, row.city)   # 2 2025-09-15 відправлено Київ
                                                        # 1 2025-09-01 отримано Київ
    print(orders_audit(session))   # [] — на демо-даних порушень немає
```

Опис складних запитів: [docs/queries.md](docs/queries.md).
