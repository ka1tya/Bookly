-- 1. SUM: кількість проданих примірників і сума всіх позицій
SELECT SUM(quantity) AS total_copies,
       SUM(quantity * unit_price) AS total_items_sum
FROM order_item;

-- 2. COUNT, SUM, AVG, MIN, MAX: статистика платежів
SELECT COUNT(*) AS payments_count,
       SUM(amount) AS total_amount,
       ROUND(AVG(amount), 2) AS avg_amount,
       MIN(amount) AS min_amount,
       MAX(amount) AS max_amount
FROM payment;

-- 3. GROUP BY: кількість і сума платежів за способом оплати
SELECT method, COUNT(*) AS payments_count, SUM(amount) AS total_amount
FROM payment
GROUP BY method
ORDER BY total_amount DESC;

-- 4. GROUP BY: сума платежів за статусом
SELECT status, COUNT(*) AS payments_count, SUM(amount) AS total_amount
FROM payment
GROUP BY status
ORDER BY status;

-- 5. HAVING: способи оплати, сума платежів за якими перевищує 1000
SELECT method, SUM(amount) AS total_amount
FROM payment
GROUP BY method
HAVING SUM(amount) > 1000;

-- 6. INNER JOIN: позиції замовлень з назвою книги та статусом платежу
SELECT oi.order_id, b.title, oi.quantity, oi.unit_price, p.status AS payment_status
FROM order_item oi
INNER JOIN book b ON b.id = oi.book_id
INNER JOIN payment p ON p.order_id = oi.order_id
ORDER BY oi.order_id;

-- 7. LEFT JOIN: усі книги та кількість проданих примірників
SELECT b.id, b.title,
       COALESCE(SUM(oi.quantity), 0) AS copies_sold
FROM book b
LEFT JOIN order_item oi ON oi.book_id = b.id
GROUP BY b.id, b.title
ORDER BY copies_sold DESC, b.title;

-- 8. RIGHT JOIN: усі замовлення та кількість позицій у кожному
SELECT o.id AS order_id, o.status,
       COUNT(oi.book_id) AS items_count
FROM order_item oi
RIGHT JOIN orders o ON o.id = oi.order_id
GROUP BY o.id, o.status
ORDER BY o.id;

-- 9. Багатотабличне групування: сума покупок кожного клієнта
SELECT c.first_name, c.last_name,
       SUM(oi.quantity * oi.unit_price) AS total_spent
FROM customer c
JOIN orders o ON o.customer_id = c.id
JOIN order_item oi ON oi.order_id = o.id
GROUP BY c.id, c.first_name, c.last_name
ORDER BY total_spent DESC;

-- 10. Багатотабличне групування: виручка за категоріями книг
SELECT cat.category_name,
       SUM(oi.quantity * oi.unit_price) AS revenue
FROM category cat
JOIN book_category bc ON bc.category_id = cat.id
JOIN order_item oi ON oi.book_id = bc.book_id
GROUP BY cat.id, cat.category_name
ORDER BY revenue DESC;

-- 11. Підзапит у WHERE: позиції, ціна яких вища за середню ціну позицій
SELECT order_id, book_id, unit_price
FROM order_item
WHERE unit_price > (SELECT AVG(unit_price) FROM order_item)
ORDER BY unit_price DESC;

-- 12. Підзапит у WHERE (IN): клієнти, які мають оплачений платіж
SELECT id, first_name, last_name
FROM customer
WHERE id IN (
    SELECT o.customer_id
    FROM orders o
    JOIN payment p ON p.order_id = o.id
    WHERE p.status = 'оплачено'
);

-- 13. Підзапит у HAVING: способи оплати з кількістю платежів вище середньої
SELECT method, COUNT(*) AS payments_count
FROM payment
GROUP BY method
HAVING COUNT(*) > (
    SELECT AVG(cnt)
    FROM (
        SELECT COUNT(*) AS cnt
        FROM payment
        GROUP BY method
    ) AS method_counts
);

-- 14. Корельований підзапит у SELECT: сума позицій і сума платежу кожного замовлення
SELECT o.id AS order_id,
       (SELECT SUM(oi.quantity * oi.unit_price)
        FROM order_item oi
        WHERE oi.order_id = o.id) AS items_total,
       (SELECT p.amount
        FROM payment p
        WHERE p.order_id = o.id) AS paid_amount
FROM orders o
ORDER BY o.id;