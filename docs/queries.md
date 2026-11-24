# Складні аналітичні запити

Кожна учасниця описує свій складний запит у форматі: бізнес-питання, SQL-запит, пояснення, приклад виводу.

## Варенко Катерина — Customer, Address

## Поліщук Анна — Category, Book

## Сітковська Аліна — Order_item, Payment

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
