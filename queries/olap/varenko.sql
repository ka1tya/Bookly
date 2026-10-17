-- Загальна кількість клієнтів у бд
SELECT COUNT(*) AS total_customers
FROM customer;

-- Загальна кількість адрес доставки в системі
SELECT COUNT(*) AS total_addresses
FROM address;

-- Середня кількість адрес на одного клієнта
SELECT AVG(address_count) AS avg_addresses_per_customer
FROM (
    SELECT customer_id, COUNT(*) AS address_count
    FROM address
    GROUP BY customer_id
) AS customer_addresses;

-- Мінімальна та максимальна кількість замовлень серед клієнтів, які вже щось замовляли
SELECT MIN(order_count) AS min_orders, MAX(order_count) AS max_orders
FROM (
    SELECT customer_id, COUNT(*) AS order_count
    FROM orders
    GROUP BY customer_id
) AS customer_orders;

-- Кількість клієнтів у кожному місті (більше одного клієнта)
SELECT a.city, COUNT(DISTINCT a.customer_id) AS customers_count
FROM address a
GROUP BY a.city
HAVING COUNT(DISTINCT a.customer_id) > 1
ORDER BY customers_count DESC;

-- Кількість замовлень у кожному місті
SELECT a.city, COUNT(o.id) AS orders_count
FROM address a
JOIN orders o ON o.address_id = a.id
GROUP BY a.city
ORDER BY orders_count DESC;

-- Запит з HAVING: клієнти, у яких більше однієї адреси доставки (використовує індекс idx_address_customer_id)
SELECT c.id, c.first_name, c.last_name, COUNT(a.id) AS address_count
FROM customer c
JOIN address a ON a.customer_id = c.id
GROUP BY c.id, c.first_name, c.last_name
HAVING COUNT(a.id) > 1
ORDER BY address_count DESC;

-- Підзапит у WHERE: клієнти з кількістю замовлень більше середньої
SELECT customer_id, COUNT(*) AS order_count
FROM orders
WHERE customer_id IN (
    SELECT customer_id
    FROM orders
    GROUP BY customer_id
    HAVING COUNT(*) > (SELECT AVG(order_count) FROM (
        SELECT customer_id, COUNT(*) AS order_count
        FROM orders
        GROUP BY customer_id
    ) AS avg_orders)
)
GROUP BY customer_id;

-- Клієнти разом з усіма їхніми адресами (INNER JOIN)
SELECT c.first_name, c.last_name, a.street, a.city, a.postal_code
FROM customer c
INNER JOIN address a ON a.customer_id = c.id
ORDER BY c.id;

-- Усі клієнти та кількість їх замовлень (LEFT JOIN)
SELECT c.first_name, c.last_name, COUNT(o.id) AS order_count
FROM customer c
LEFT JOIN orders o ON o.customer_id = c.id
GROUP BY c.id
ORDER BY order_count DESC;

-- Той самий результат, але з RIGHT JOIN (зберігає всіх клієнтів, навіть без замовлень)
SELECT c.first_name, c.last_name, COUNT(o.id) AS order_count
FROM orders o
RIGHT JOIN customer c ON o.customer_id = c.id
GROUP BY c.id
ORDER BY order_count DESC;

-- Сума платежів по кожному місту доставки
SELECT a.city, SUM(p.amount) AS total_payments
FROM address a
JOIN orders o ON o.address_id = a.id
JOIN payment p ON p.order_id = o.id
GROUP BY a.city
ORDER BY total_payments DESC;

-- Підзапит у WHERE: клієнти, що оформили більше одного замовлення, разом із кількістю їхніх замовлень
SELECT customer_id, COUNT(*) AS order_count
FROM orders
WHERE customer_id IN (
    SELECT customer_id
    FROM orders
    GROUP BY customer_id
    HAVING COUNT(*) > 1
)
GROUP BY customer_id
ORDER BY order_count DESC;

-- Підзапит з HAVING: міста з кількістю клієнтів більше середньої
SELECT a.city, COUNT(DISTINCT a.customer_id) AS customers_count
FROM address a
GROUP BY a.city
HAVING COUNT(DISTINCT a.customer_id) > (
    SELECT AVG(city_count) FROM (
        SELECT COUNT(DISTINCT customer_id) AS city_count
        FROM address
        GROUP BY city
    ) AS avg_per_city
);

-- Підзапит у SELECT: кількість замовлень для кожного клієнта
SELECT c.first_name, c.last_name,
    (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.id) AS order_count
FROM customer c
ORDER BY order_count DESC;