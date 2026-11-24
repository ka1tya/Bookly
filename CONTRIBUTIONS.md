# Внески команди

Робота ведеться в окремих гілках і потрапляє в `main` через pull request із code review.

## Варенко Катерина — Customer, Address

- Перебудувала репозиторій під курсову: схема бази розбита на міграції `migrations/001-003`, вимоги перенесено в `docs/requirements.md`
- Основа застосунку на Python: ORM-моделі SQLAlchemy для всіх 9 таблиць, підключення до бази, спільні статуси й базові помилки
- Налаштування pytest і тестова фікстура з відкатом транзакції після кожного тесту
- Налаштувала Docker Compose: робоча й окрема тестова бази PostgreSQL з автоматичними міграціями, pgAdmin, контейнер застосунку
- Сценарії (`src/services/customer_service.py`):
  - `register_customer` — клієнт разом з адресами в одній транзакції, перевірка дубліката email і телефону;
  - `change_order_address` — зміна адреси замовлення з блокуванням `FOR UPDATE`;
  - `delete_customer` — видалення клієнта без замовлень, адреси видаляються через `ON DELETE CASCADE`;
  - `check_address_owner` — перевірка, що адреса належить клієнту (використовується в `create_order`).
- Запити (`src/repositories/customer_repository.py`): `find_by_email`, `addresses_in_city`, складний `sales_by_city` (CTE, підзапит)
- Тести: `test/unit/test_customer_validation.py`, `test/integration/test_customer_scenarios.py`, `test/integration/test_customer_queries.py`
- Демо `src/demo_customer.py`, опис складного запиту в `docs/queries.md`

## Поліщук Анна — Category, Book

- Сценарії (`src/services/book_service.py`):
  - `create_book_with_categories` — книга разом з категоріями в одній транзакції;
  - `change_book_price` — зміна ціни з блокуванням `FOR UPDATE`;
  - `delete_book_not_in_orders` — видалення книги, якої немає в замовленнях;
  - `get_current_prices` — поточні ціни книг (використовується в `create_order`).
- Запити (`src/repositories/book_queries.py`): `search_by_title`, `books_in_category`, складний `book_revenue_ranking` (CTE, `RANK() OVER`)
- Тести: `test/unit/test_book_validation.py`, `test/unit/test_book_pagination.py`, `test/integration/test_book.py`, `test/integration/test_book_queries.py`
- Демо `src/demo_book.py`, опис складного запиту в `docs/queries.md`
- Документація схеми `docs/schema.md` і ER-діаграма `docs/ER-diagram.png`

## Сітковська Аліна — Order_item, Payment

- Фабрики тестових даних у `test/conftest.py`
- Сценарії (`src/services/payment_service.py`):
  - `add_items_to_order` — додавання позицій у замовлення і створення або перерахунок платежу;
  - `confirm_cash_payment` — підтвердження оплати готівкою після отримання замовлення, блокування замовлення й платежу;
  - `remove_order_item` — видалення позиції з нового замовлення з перерахунком суми платежу;
  - `add_items`, `create_pending_payment` — допоміжні функції без commit (використовуються в `create_order`).
- Запити (`src/repositories/payment_queries.py`): `payments_by_status_and_method`, `order_items_with_titles`, складний `monthly_payments_report` (CTE, `SUM() OVER`, `RANK() OVER`)
- Тести: `test/unit/test_payment_validation.py`, `test/unit/test_payment_pagination.py`, `test/integration/test_payment.py`, `test/integration/test_payment_queries.py`
- Демо `src/demo_payment.py`, опис складного запиту в `docs/queries.md`

## Лобода Аліна — Author, Orders

- Допустимі переходи статусів замовлення `ALLOWED_TRANSITIONS` у `src/models/constants.py`
- Сценарії (`src/services/order_service.py`):
  - `create_order` — замовлення, позиції й платіж в одній транзакції з перевіркою клієнта, адреси й книг;
  - `change_order_status` — зміна статусу з блокуванням `FOR UPDATE` і перевіркою допустимого переходу;
  - `delete_cancelled_order` — видалення скасованого замовлення разом з позиціями й платежем.
- Запити (`src/repositories/order_repository.py`): `search_authors`, `customer_orders`, складний `orders_audit` (CTE, `LEFT JOIN`, `CASE`)
- Тести: `test/unit/test_order_status.py`, `test/unit/test_order_pagination.py`, `test/unit/test_order_items_validation.py`, `test/integration/test_order.py`, `test/integration/test_order_queries.py`, `test/integration/test_create_order.py`
- Опис складного запиту в `docs/queries.md`, приклади використання в `README.md`, `CONTRIBUTIONS.md`

