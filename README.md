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

## Налаштування та запуск

## Запуск тестів

## Структура

```
Bookly/
├── docs/
│   ├── requirements.md      вимоги, бізнес-правила, сутності
│   ├── schema.md            опис таблиць, індексів, рішень
│   ├── queries.md           складні аналітичні запити
│   └── ER-diagram.png
├── migrations/
│   ├── 001_initial_schema.sql   таблиці
│   ├── 002_add_indexes.sql      індекси
│   └── 003_seed_test_data.sql   демо-дані
├── README.md
└── CONTRIBUTIONS.md
```

## Приклади використання
