# Опис схеми бази даних

СУБД: PostgreSQL. Схема містить 9 таблиць, їх повний скрипт створення й тестових даних у `schema.sql`.

## Таблиці

### customer

| Колонка      | Тип          | Обмеження        |
| ------------ | ------------ | ---------------- |
| `id`         | SERIAL       | PK               |
| `first_name` | VARCHAR(100) | NOT NULL         |
| `last_name`  | VARCHAR(100) | NOT NULL         |
| `email`      | VARCHAR(255) | NOT NULL, UNIQUE |
| `phone`      | VARCHAR(20)  | NOT NULL, UNIQUE |

### address

| Колонка           | Тип          | Обмеження                                           |
| ----------------- | ------------ | --------------------------------------------------- |
| `id`              | SERIAL       | PK                                                  |
| `customer_id`     | INTEGER      | NOT NULL, FK -> `customer(id)`, `ON DELETE CASCADE` |
| `country`, `city` | VARCHAR(100) | NOT NULL                                            |
| `street`          | VARCHAR(255) | NOT NULL                                            |
| `postal_code`     | VARCHAR(20)  | необов'язкове                                       |

## Пояснення ключових рішень

- `postal_code` має текстовий тип даних `VARCHAR()`, щоб зберігати нулі на початку (`02291`);

## Індекси

- `idx_address_customer_id`;

## Тестові дані
