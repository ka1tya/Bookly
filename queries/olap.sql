-- =====================================================================
-- Поліщук Анна - OLAP-запити для бази даних Bookly
-- =====================================================================

-- Загальна кількість книг у каталозі
SELECT COUNT(*) AS total_books
FROM book;

-- Середня ціна книги в каталозі
SELECT AVG(price) AS avg_price
FROM book;

-- Мінімальна та максимальна ціна книги для кожного автора
SELECT author_id, MIN(price) AS min_price, MAX(price) AS max_price
FROM book
GROUP BY author_id
ORDER BY author_id;

-- Кількість книг у кожній категорії (більше однієї книги)
SELECT c.category_name, COUNT(bc.fk_book_id) AS books_count
FROM category c
JOIN book_category bc ON bc.fk_category_id = c.category_id
GROUP BY c.category_name
HAVING COUNT(bc.fk_book_id) > 1
ORDER BY books_count DESC;

-- INNER JOIN: книги разом з їхніми категоріями
SELECT b.title, c.category_name
FROM book b
INNER JOIN book_category bc ON bc.fk_book_id = b.book_id
INNER JOIN category c       ON c.category_id = bc.fk_category_id
ORDER BY b.title;

-- LEFT JOIN: усі книги, навіть без категорій
SELECT b.title, c.category_name
FROM book b
LEFT JOIN book_category bc ON bc.fk_book_id = b.book_id
LEFT JOIN category c       ON c.category_id = bc.fk_category_id
ORDER BY b.title;

-- LEFT JOIN у зворотному напрямку: усі категорії, навіть порожні
SELECT c.category_name, b.title
FROM category c
LEFT JOIN book_category bc ON bc.fk_category_id = c.category_id
LEFT JOIN book b            ON b.book_id = bc.fk_book_id
ORDER BY c.category_name;

-- Підзапит у WHERE: книги дорожчі за середню ціну
SELECT title, price
FROM book
WHERE price > (SELECT AVG(price) FROM book)
ORDER BY price DESC;

-- Підзапит у SELECT: кількість категорій для кожної книги
SELECT
    b.title,
    (SELECT COUNT(*) FROM book_category bc WHERE bc.fk_book_id = b.book_id) AS categories_count
FROM book b
ORDER BY categories_count DESC, b.title;

-- Підзапит у WHERE з IN: категорії з дорогими книгами
SELECT category_name
FROM category
WHERE category_id IN (
    SELECT bc.fk_category_id
    FROM book_category bc
    JOIN book b ON b.book_id = bc.fk_book_id
    WHERE b.price > 300
)
ORDER BY category_name;

-- Варенко Катерина - OLAP-запити 
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