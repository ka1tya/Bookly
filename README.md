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
