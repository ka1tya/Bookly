# Внесок учасників

Проєкт bookly виконується командою з 4 осіб. Нижче — розподіл
відповідальності за сутностями бази даних, включно з інтерв'юванням
стейкхолдера для своєї частини (Лаб 1) та подальшою реалізацією (Лаб 2+).

## Команда

| Учасник          | Сутності            | Основні питання інтерв'ю                                                             |
| ---------------- | ------------------- | ------------------------------------------------------------------------------------ |
| Варенко Катерина | Customer, Address   | Які дані про клієнта потрібні? Чи може клієнт мати кілька адрес?                     |
| Поліщук Анна     | Category, Book      | Як організований каталог книг? Чи може книга бути в кількох категоріях?              |
| Лобода Аліна     | Author, Orders      | Чи потрібна інформація про авторів? Який у замовлення статус і які переходи можливі? |
| Сітковська Аліна | Order_item, Payment | Як формується ціна в замовленні? Які способи оплати та статуси платежу?              |

## Сутності та зв'язки за учасниками

### Варенко Катерина — Customer, Address

- Customer (id PK, first_name, last_name, email, phone)
- Address (id PK, customer_id FK, country, city, street, postal_code)
- Зв'язки: Customer–Address (1:N), Customer–Orders (1:N, описано з боку Customer)

### Поліщук Анна — Category, Book

- Category (id PK, name)
- Book (id PK, author_id FK, title, published_year, price)
- Book_category (book_id PK/FK, category_id PK/FK): асоціативна таблиця зв'язку Category–Book
- Зв'язки: Category–Book (N:N), Author–Book (1:N — зв'язок описано з боку Book)

### Лобода Аліна — Author, Orders

- Author (id PK, first_name, last_name)
- Orders (id PK, customer_id FK, address_id FK, date, status)
- Зв'язки: Author–Book (1:N — з боку Author), Address–Orders (1:N), Customer–Orders (1:N — з боку Orders)

### Сітковська Аліна — Order_item, Payment

- Order_item (order_id PK/FK, book_id PK/FK, quantity, unit_price)
- Payment (id PK, order_id FK, amount, date, method, status)
- Зв'язки: Orders–Order_item (1:N), Book–Order_item (1:N), Orders–Payment (1:1)

## Спільні файли та відповідальні

| Файл                                                         | Хто веде                                                    | Як вносяться зміни                                                          |
| ------------------------------------------------------------ | ----------------------------------------------------------- | --------------------------------------------------------------------------- |
| `README.md` (вимоги, бізнес-правила, діаграма)               | усі, кожен свої розділи                                     | комміт у `main` по черзі                                                    |
| `database/schema.sql`                                        | усі, кожен свої розділи                                     | комміт у `main`; після змін база перестворюється (`docker compose down -v`) |
| `docs/queries.md`                                            | усі, кожен свій розділ                                      | комміт у `main`                                                             |
| `docs/schema.md`                                             | Варенко Катерина та Поліщук Анна, інші просять внести зміни | комміт у `main`                                                             |
| `docker-compose.yml`                                         | Варенко Катерина, решта робить review                       | окрема гілка та pull request                                                |
| `queries/oltp/<прізвище>.sql`, `queries/olap/<прізвище>.sql` | кожен свій файл                                             | власна гілка та pull request                                                |

Спільні документи та схему ведемо в `main`, щоб уникнути конфліктів між
учасниками, які редагують одні й ті самі файли. Власні файли із запитами
та налаштування Docker вносимо через гілки й pull request із review.
