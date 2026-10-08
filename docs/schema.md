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

### category

| Колонка         | Тип          | Обмеження        |
| --------------- | ------------ | ---------------- |
| `category_id`   | SERIAL       | PK               |
| `category_name` | VARCHAR(60)  | NOT NULL, UNIQUE |

### book

| Колонка          | Тип           | Обмеження                                     |
| ---------------- | ------------- | ---------------------------------------------- |
| `book_id`        | SERIAL        | PK                                              |
| `author_id`      | INTEGER       | NOT NULL, FK -> `author(author_id)`             |
| `title`          | VARCHAR(200)  | NOT NULL                                        |
| `published_year` | INTEGER       | CHECK (`published_year > 0`)                    |
| `price`          | NUMERIC(10,2) | NOT NULL, CHECK (`price >= 0`)                  |

### book_category

| Колонка           | Тип     | Обмеження                                                      |
| ------------------ | ------- | ---------------------------------------------------------------- |
| `fk_book_id`       | INTEGER | NOT NULL, FK -> `book(book_id)`, частина складеного PK           |
| `fk_category_id`   | INTEGER | NOT NULL, FK -> `category(category_id)`, частина складеного PK   |

Складений первинний ключ `(fk_book_id, fk_category_id)` реалізує зв'язок "багато до багатьох" між книгами та категоріями — одна книга може належати до кількох категорій, одна категорія містить багато книг.

## Пояснення ключових рішень

- `postal_code` має текстовий тип даних `VARCHAR()`, щоб зберігати нулі на початку (`02291`);
- `price` має тип `NUMERIC(10,2)`, а не `FLOAT`, щоб уникнути похибок округлення під час роботи з грошовими сумами;
- `CHECK (price >= 0)` і `CHECK (published_year > 0)` захищають від некоректних даних на рівні бази, а не лише на рівні застосунку;
- `category_name` позначено `UNIQUE`, щоб виключити дублікати категорій з однаковою назвою;
- зв'язок `Category`–`Book` реалізовано через окрему таблицю `book_category`, оскільки це зв'язок "багато до багатьох", а не через зовнішній ключ напряму.


## Індекси

- `idx_address_customer_id`;
- `idx_book_author_id` — індекс на `book.author_id` для прискорення `JOIN` з таблицею `author`.


## Тестові дані

### category

| category_id | category_name       |
|---|---|
| 1 | Фентезі |
| 2 | Детектив |
| 3 | Жахи |
| 4 | Поезія |
| 5 | Наукова фантастика |
| 6 | Трилер |
| 7 | Романтика |

### book

| book_id | author_id | title | published_year | price |
|---|---|---|---|---|
| 1 | 1 | Гаррі Поттер і філософський камінь | 1997 | 350.00 |
| 2 | 2 | Бійцівський клуб | 1996 | 300.00 |
| 3 | 3 | Воно | 1986 | 420.00 |
| 4 | 4 | Маруся Чурай | 1979 | 200.00 |
| 5 | 5 | Кобзар | 1840 | 180.00 |
| 6 | 6 | Вбивство у Східному експресі | 1934 | 260.00 |
| 7 | 7 | Переслідування Аделіни | 2021 | 430.00 |

### book_category

| fk_book_id | fk_category_id |
|---|---|
| 1 | 1 |
| 2 | 6 |
| 3 | 3 |
| 3 | 6 |
| 4 | 4 |
| 5 | 4 |
| 6 | 2 |
| 7 | 6 |
| 7 | 7 |
