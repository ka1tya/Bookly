# Складні аналітичні запити

Кожна учасниця описує свій складний запит у форматі: бізнес-питання, SQL-запит, пояснення, приклад виводу.

## Варенко Катерина — Customer, Address

### Бізнес-питання

У яких містах магазин продає найбільше книжок і яку частку всієї виручки дає кожне місто?

Магазину треба знати, звідки приходить найбільше замовлень і грошей, щоб вирішувати, куди спрямувати більше реклами та де варто відкрити фізичний магазин. Скасовані замовлення не враховуються, бо по суті за них магазин грошей не отримав.

### SQL-запит

Функція `sales_by_city()` у `src/repositories/customer_repository.py`

```sql
WITH city_sales AS (
    SELECT a.city,
           COUNT(DISTINCT o.customer_id) AS customers,
           COUNT(DISTINCT o.id) AS orders,
           SUM(oi.quantity * oi.unit_price) AS revenue
    FROM address a
    JOIN orders o ON o.address_id = a.id
    JOIN order_item oi ON oi.order_id = o.id
    WHERE o.status <> 'скасовано'
    GROUP BY a.city
)
SELECT city,
       customers,
       orders,
       revenue,
       ROUND(revenue / orders, 2) AS average_order,
       ROUND(100 * revenue / (SELECT SUM(revenue) FROM city_sales), 1) AS revenue_share
FROM city_sales
ORDER BY revenue DESC;
```

### Пояснення

- СТЕ `city_sales` рахує для кожного міста кількість клієнтів, замовлень і виручку `SUM(quantity * unit_price)`. Береться `unit_price` з `order_item`, тобто ціна на момент замовлення, а не поточна ціна книги;
- Таблиці `address`, `orders` та `order_item` з'єднані через `JOIN` (адреса доставки -> замовлення -> позиції замовлення). Місто береться з адреси доставки замовлення;
- Скасовані замовлення не враховуються (`o.status <> 'скасовано'`);
- `COUNT(DISTINCT ...)` рахує кожного клієнта й кожне замовлення лише один раз, оскільки після `JOIN` з `order_item` одне замовлення з кількома книгами повторюється декілька разів, і без `DISTINCT` його було б повторно пораховано;
- Середній чек (`average_order`) - виручка, поділена на кількість замовлень, рахується в основному запиті з готових підсумків СТЕ;
- Підзапит `(SELECT SUM(revenue) FROM city_sales)` дає загальну виручку всіх міст, тому `revenue_share` показує частку міста у відсотках;
- Міста сортуються від найбільшої виручки.

### Приклад виводу

Демо-дані, `python -m src.demo_customer`:

| city     | customers | orders | revenue | average_order | revenue_share |
| -------- | --------- | ------ | ------- | ------------- | ------------- |
| Київ     | 1         | 2      | 950.00  | 475.00        | 67.4          |
| Одеса    | 1         | 1      | 260.00  | 260.00        | 18.4          |
| Нью-Йорк | 1         | 1      | 200.00  | 200.00        | 14.2          |

## Поліщук Анна — Category, Book

### Бізнес-питання

Які книги найприбутковіші в кожній категорії?

Магазину треба знати, які книги приносять найбільше грошей у своїй категорії, щоб вирішувати, що закуповувати і що ставити на головну сторінку категорії. Книги, які ще не продавались, теж показуються, щоб було видно, що в категорії не продається.

### SQL-запит

Функція `book_revenue_ranking()` у `src/repositories/book_queries.py`.

```sql
WITH book_sales AS (
    SELECT oi.book_id,
           SUM(oi.quantity) AS sold,
           SUM(oi.quantity * oi.unit_price) AS revenue
    FROM order_item oi
    JOIN orders o ON o.id = oi.order_id
    WHERE o.status <> 'скасовано'
    GROUP BY oi.book_id
)
SELECT c.category_name,
       b.title,
       COALESCE(s.sold, 0) AS sold,
       COALESCE(s.revenue, 0) AS revenue,
       RANK() OVER (PARTITION BY c.id ORDER BY COALESCE(s.revenue, 0) DESC) AS place
FROM category c
JOIN book_category bc ON bc.category_id = c.id
JOIN book b ON b.id = bc.book_id
LEFT JOIN book_sales s ON s.book_id = b.id
ORDER BY c.category_name, place, b.title;
```

### Пояснення

- **CTE `book_sales`** рахує для кожної книги кількість проданих примірників і виручку `SUM(quantity * unit_price)`. Береться `unit_price` з `order_item`, тобто ціна на момент замовлення, а не поточна ціна книги.
- **Скасовані замовлення** не враховуються (`o.status <> 'скасовано'`), бо за них магазин грошей не отримав.
- **5 таблиць:** `order_item` і `orders` у CTE, а `category`, `book_category`, `book` в основному запиті. Через `book_category` книга з кількома категоріями потрапляє в рейтинг кожної з них (наприклад, «Воно» є і в «Жахах», і в «Трилері»).
- **`LEFT JOIN`** залишає книги без продажів, а `COALESCE(..., 0)` ставить їм 0 замість `NULL`.
- **`RANK() OVER (PARTITION BY c.id ...)`** нумерує книги окремо в кожній категорії від найбільшої виручки. Книги з однаковою виручкою отримують однакове місце, а наступне місце пропускається (1, 2, 2, а далі було б 4). `ROW_NUMBER()` дав би їм різні місця випадково, тому тут обрано `RANK()`.
- Категорії без жодної книги («Наукова фантастика») у результат не потрапляють, бо їх відсікає `JOIN book_category`.

### Приклад виводу

Демо-дані, `python -m src.demo_book`:

| category_name | title | sold | revenue | place |
|---|---|---|---|---|
| Детектив | Вбивство у Східному експресі | 1 | 260.00 | 1 |
| Жахи | Воно | 0 | 0 | 1 |
| Поезія | Маруся Чурай | 1 | 200.00 | 1 |
| Поезія | Кобзар | 0 | 0 | 2 |
| Романтика | Переслідування Аделіни | 0 | 0 | 1 |
| Трилер | Бійцівський клуб | 2 | 600.00 | 1 |
| Трилер | Воно | 0 | 0 | 2 |
| Трилер | Переслідування Аделіни | 0 | 0 | 2 |
| Фентезі | Гаррі Поттер і філософський камінь | 1 | 350.00 | 1 |

«Переслідування Аделіни» має виручку 0, бо її єдине замовлення скасоване. «Воно» і «Переслідування Аделіни» ділять друге місце в «Трилері».

## Сітковська Аліна — Order_item, Payment

### Бізнес-питання

Як змінюється виручка за місяцями і який спосіб оплати переважає?

Магазину треба бачити динаміку грошей за місяцями окремо для картки й готівки, накопичену суму по кожному способу та те, який спосіб приніс більше у конкретному місяці. Це допомагає вирішувати, чи розвивати онлайн-оплату, чи тримати готівку при отриманні.

### SQL-запит

Функція `monthly_payments_report()` у `src/repositories/payment_queries.py`.

```sql
WITH monthly AS (
    SELECT DATE_TRUNC('month', p.date)::date AS month,
           p.method,
           COUNT(*) AS payments_count,
           SUM(p.amount) AS total_amount
    FROM payment p
    JOIN orders o ON o.id = p.order_id
    WHERE o.status <> 'скасовано'
    GROUP BY DATE_TRUNC('month', p.date), p.method
)
SELECT month,
       method,
       payments_count,
       total_amount,
       SUM(total_amount) OVER (PARTITION BY method ORDER BY month) AS cumulative_amount,
       RANK() OVER (PARTITION BY month ORDER BY total_amount DESC) AS place
FROM monthly
ORDER BY month, place, method;
```

### Пояснення

- **CTE `monthly`** групує платежі за місяцем і способом оплати та рахує кількість платежів `COUNT(*)` і суму `SUM(amount)`. `DATE_TRUNC('month', date)` обрізає дату до першого числа місяця, тому всі платежі одного місяця потрапляють в одну групу.
- **Скасовані замовлення** не враховуються (`o.status <> 'скасовано'`), бо за них гроші не надходять. Для цього платіж з'єднується з `orders`.
- **Накопичувальна сума** `SUM(total_amount) OVER (PARTITION BY method ORDER BY month)` додає до суми поточного місяця суми всіх попередніх місяців того самого способу. Вікно не згортає рядки, на відміну від `GROUP BY`.
- **`RANK() OVER (PARTITION BY month ORDER BY total_amount DESC)`** нумерує способи оплати всередині місяця від більшої суми до меншої. Місце 1 це спосіб, що переважає в цьому місяці. При однакових сумах обидва способи отримують місце 1.
- Платежі враховуються незалежно від статусу («очікує» і «оплачено»), бо запит показує оформлені платежі. Щоб бачити лише отримані гроші, достатньо додати `p.status = 'оплачено'`.

### Приклад виводу

Демо-дані, `python -m src.demo_payment`:

| month | method | payments_count | total_amount | cumulative_amount | place |
|---|---|---|---|---|---|
| 2025-09-01 | готівка | 1 | 600.00 | 600.00 | 1 |
| 2025-09-01 | картка | 2 | 550.00 | 550.00 | 2 |
| 2025-10-01 | готівка | 1 | 260.00 | 860.00 | 1 |

У вересні готівка (600) випередила картку (550), хоча карткою платежів більше. Платіж карткою на 860 грн за жовтень не потрапив у звіт, бо його замовлення скасоване.

## Лобода Аліна — Author, Orders

### Бізнес-питання

Які замовлення мають помилки в даних?

Частину правил магазину база сама не перевіряє: замовлення не може бути порожнім, у кожного замовлення має бути платіж, сума платежу має дорівнювати сумі позицій, а готівку можна вважати оплаченою лише після отримання замовлення. Запит знаходить замовлення, де якесь із цих правил порушене, щоб менеджер міг їх виправити.

### SQL-запит

Функція `orders_audit()` у `src/repositories/order_repository.py`.

```sql
WITH order_totals AS (
    SELECT order_id,
           COUNT(*) AS items_count,
           SUM(quantity * unit_price) AS items_total
    FROM order_item
    GROUP BY order_id
),
audit AS (
    SELECT o.id AS order_id,
           o.status,
           COALESCE(t.items_count, 0) AS items_count,
           COALESCE(t.items_total, 0) AS items_total,
           p.amount AS paid_amount,
           p.method,
           p.status AS payment_status,
           CASE WHEN t.order_id IS NULL THEN true ELSE false END AS empty_order,
           CASE WHEN p.id IS NULL THEN true ELSE false END AS no_payment,
           CASE WHEN p.amount <> COALESCE(t.items_total, 0) THEN true ELSE false END AS amount_mismatch,
           CASE WHEN p.method = 'готівка' AND p.status = 'оплачено' AND o.status <> 'отримано'
                THEN true ELSE false END AS cash_paid_early
    FROM orders o
    LEFT JOIN order_totals t ON t.order_id = o.id
    LEFT JOIN payment p ON p.order_id = o.id
)
SELECT *
FROM audit
WHERE empty_order OR no_payment OR amount_mismatch OR cash_paid_early
ORDER BY order_id;
```

### Пояснення

- **CTE `order_totals`** рахує для кожного замовлення кількість позицій `COUNT(*)` і суму `SUM(quantity * unit_price)`.
- **CTE `audit`** бере всі замовлення і приєднує до них суми та платіж через `LEFT JOIN`. `LEFT` потрібен, щоб не загубити замовлення без позицій або без платежу: у них відповідні поля будуть `NULL`.
- **Чотири `CASE`** — це чотири правила: порожнє замовлення, немає платежу, сума платежу не дорівнює сумі позицій, готівку оплачено до отримання. Кожне дає `true`, якщо правило порушене.
- **`COALESCE(..., 0)`** ставить 0 замість `NULL` для замовлень без позицій.
- **Фінальний `WHERE`** залишає лише замовлення, де хоча б одне правило порушене.
- Використано 3 таблиці (`orders`, `order_item`, `payment`), 2 CTE, агрегати і `CASE`.

### Приклад виводу

На демо-даних порушень немає, тому запит повертає порожній результат. Якщо в тестовій базі змінити суму платежу замовлення №3 на 999, позначити готівку замовлення №2 як оплачену й створити замовлення без позицій, результат буде такий:

| order_id | status | items_count | items_total | paid_amount | empty_order | no_payment | amount_mismatch | cash_paid_early |
|---|---|---|---|---|---|---|---|---|
| 2 | відправлено | 1 | 600.00 | 600.00 | false | false | false | true |
| 3 | збирається | 1 | 200.00 | 999.00 | false | false | true | false |
| 6 | нове | 0 | 0 | NULL | true | true | false | false |

Замовлення №2 ще не отримане, а готівку вже позначено оплаченою. У №3 сума платежу не збігається із сумою товарів. №6 порожнє і без платежу.
