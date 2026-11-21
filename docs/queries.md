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

## Сітковська Аліна — Order_item, Payment

## Лобода Аліна — Author, Orders
