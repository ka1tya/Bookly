
-- 1. COUNT: кількість замовлень
SELECT COUNT(*) AS total_orders
FROM orders;

-- 2. MIN, MAX: найраніша й найпізніша дата замовлення
SELECT MIN(date) AS first_order_date, MAX(date) AS last_order_date
FROM orders;

-- 3. SUM, AVG: загальна виручка й середня сума замовлення (підзапит у FROM)
SELECT SUM(order_total) AS total_revenue,
       ROUND(AVG(order_total), 2) AS avg_order_total
FROM (
    SELECT order_id, SUM(quantity * unit_price) AS order_total
    FROM order_item
    GROUP BY order_id
) AS order_totals;

-- 4. GROUP BY: кількість замовлень за статусами
SELECT status, COUNT(*) AS orders_count
FROM orders
GROUP BY status
ORDER BY orders_count DESC, status;

-- 5. GROUP BY: кількість замовлень за місяцями
SELECT TO_CHAR(date, 'YYYY-MM') AS month, COUNT(*) AS orders_count
FROM orders
GROUP BY TO_CHAR(date, 'YYYY-MM')
ORDER BY month;

-- 6. HAVING: клієнти з більш ніж одним замовленням
SELECT customer_id, COUNT(*) AS orders_count
FROM orders
GROUP BY customer_id
HAVING COUNT(*) > 1;

-- 7. HAVING + JOIN: автори, чия виручка перевищує 300
SELECT a.first_name, a.last_name,
       SUM(oi.quantity * oi.unit_price) AS revenue
FROM author a
JOIN book b ON b.author_id = a.id
JOIN order_item oi ON oi.book_id = b.id
GROUP BY a.id, a.first_name, a.last_name
HAVING SUM(oi.quantity * oi.unit_price) > 300
ORDER BY revenue DESC;

-- 8. INNER JOIN: замовлення з клієнтом, містом доставки та платежем
SELECT o.id AS order_id, o.date, o.status,
       c.first_name || ' ' || c.last_name AS customer,
       a.city, p.amount, p.method
FROM orders o
INNER JOIN customer c ON c.id = o.customer_id
INNER JOIN address a ON a.id = o.address_id
INNER JOIN payment p ON p.order_id = o.id
ORDER BY o.id;

-- 9. LEFT JOIN: усі автори та кількість проданих примірників їхніх книг
SELECT a.id, a.first_name, a.last_name,
       COALESCE(SUM(oi.quantity), 0) AS copies_sold
FROM author a
LEFT JOIN book b ON b.author_id = a.id
LEFT JOIN order_item oi ON oi.book_id = b.id
GROUP BY a.id, a.first_name, a.last_name
ORDER BY copies_sold DESC, a.last_name;

-- 10. RIGHT JOIN: усі адреси та кількість замовлень на кожну
SELECT ad.id AS address_id, ad.city, ad.street,
       COUNT(o.id) AS orders_count
FROM orders o
RIGHT JOIN address ad ON ad.id = o.address_id
GROUP BY ad.id, ad.city, ad.street
ORDER BY orders_count DESC, ad.id;

-- 11. FULL JOIN: узгодженість замовлень і платежів
SELECT o.id AS order_id, p.id AS payment_id, p.status AS payment_status
FROM orders o
FULL JOIN payment p ON p.order_id = o.id
ORDER BY o.id;

-- 12. Багатотабличне групування: сума й кількість позицій кожного замовлення
SELECT o.id AS order_id, o.status,
       SUM(oi.quantity) AS items_count,
       SUM(oi.quantity * oi.unit_price) AS order_total
FROM orders o
JOIN order_item oi ON oi.order_id = o.id
GROUP BY o.id, o.status
ORDER BY o.id;

-- 13. Підзапит у WHERE (IN): замовлення з неоплаченим платежем
SELECT id, customer_id, date, status
FROM orders
WHERE id IN (
    SELECT order_id
    FROM payment
    WHERE status = 'очікує'
)
ORDER BY id;

-- 14. Підзапит у HAVING: замовлення, сума яких вища за середню
SELECT o.id AS order_id,
       SUM(oi.quantity * oi.unit_price) AS order_total
FROM orders o
JOIN order_item oi ON oi.order_id = o.id
GROUP BY o.id
HAVING SUM(oi.quantity * oi.unit_price) > (
    SELECT AVG(order_total)
    FROM (
        SELECT SUM(quantity * unit_price) AS order_total
        FROM order_item
        GROUP BY order_id
    ) AS order_totals
)
ORDER BY order_total DESC;

-- 15. Корельований підзапит у SELECT: проданих примірників на кожного автора
SELECT a.id, a.first_name, a.last_name,
       (SELECT COALESCE(SUM(oi.quantity), 0)
        FROM order_item oi
        JOIN book b ON b.id = oi.book_id
        WHERE b.author_id = a.id) AS copies_sold
FROM author a
ORDER BY copies_sold DESC, a.id;