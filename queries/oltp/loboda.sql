SELECT 'author' AS table_name, COUNT(*) AS rows_count FROM author
UNION ALL SELECT 'customer', COUNT(*) FROM customer
UNION ALL SELECT 'address', COUNT(*) FROM address
UNION ALL SELECT 'category', COUNT(*) FROM category
UNION ALL SELECT 'book', COUNT(*) FROM book
UNION ALL SELECT 'book_category', COUNT(*) FROM book_category
UNION ALL SELECT 'orders', COUNT(*) FROM orders
UNION ALL SELECT 'order_item', COUNT(*) FROM order_item
UNION ALL SELECT 'payment', COUNT(*) FROM payment
ORDER BY table_name;


-- SELECT


-- 1. Усі автори
SELECT * FROM author;

-- 2. Пошук автора за прізвищем (лише потрібні стовпці)
SELECT id, first_name, last_name
FROM author
WHERE last_name = 'Кінг';

-- 3. Нові замовлення
SELECT id, customer_id, address_id, date, status
FROM orders
WHERE status = 'нове';

-- 4. Замовлення, доставлені в Київ, з іменем клієнта
SELECT o.id, o.date, o.status, c.first_name, c.last_name, a.city
FROM orders o
JOIN customer c ON c.id = o.customer_id
JOIN address a ON a.id = o.address_id
WHERE a.city = 'Київ'
ORDER BY o.date;


-- INSERT


-- 5. Новий автор
INSERT INTO author (first_name, last_name)
VALUES ('Оксана', 'Забужко');

-- перевірка
SELECT * FROM author WHERE last_name = 'Забужко';

-- Запити 6-8: одне нове замовлення клієнтки №5 в одній транзакції
-- (замовлення не може бути порожнім). Виконувати разом, від BEGIN до COMMIT.
BEGIN;

-- 6. Нове замовлення на адресу №6 (власна адреса клієнтки)
INSERT INTO orders (customer_id, address_id)
VALUES (5, 6);

-- 7. Позиція замовлення (ціна фіксується з каталогу в unit_price)
INSERT INTO order_item (order_id, book_id, quantity, unit_price)
SELECT o.id, b.id, 2, b.price
FROM orders o, book b
WHERE o.customer_id = 5 AND b.title = 'Кобзар';

-- 8. Платіж за це замовлення
INSERT INTO payment (order_id, amount, method)
SELECT o.id, 2 * b.price, 'картка'
FROM orders o, book b
WHERE o.customer_id = 5 AND b.title = 'Кобзар';

COMMIT;

-- перевірка
SELECT * FROM orders WHERE customer_id = 5;



-- UPDATE


-- 9. Уточнити ім'я автора
UPDATE author
SET first_name = 'Оксана Стефанівна'
WHERE last_name = 'Забужко';

-- 10. Передати нове замовлення на збирання
UPDATE orders
SET status = 'збирається'
WHERE customer_id = 5 AND status = 'нове';

-- 11. Позначити платіж за це замовлення як оплачений
UPDATE payment
SET status = 'оплачено'
WHERE order_id = (SELECT id FROM orders WHERE customer_id = 5);

-- перевірка
SELECT * FROM orders WHERE customer_id = 5;
SELECT * FROM payment WHERE status = 'оплачено';


-- DELETE


-- Запити 12-14: видалення замовлення. Спочатку дочірні таблиці, потім orders
-- (зовнішні ключі без CASCADE). Виконувати разом, від BEGIN до COMMIT.
BEGIN;

-- 12. Видалити платіж замовлення
DELETE FROM payment
WHERE order_id IN (SELECT id FROM orders WHERE customer_id = 5);

-- 13. Видалити позиції замовлення
DELETE FROM order_item
WHERE order_id IN (SELECT id FROM orders WHERE customer_id = 5);

-- 14. Видалити саме замовлення
DELETE FROM orders
WHERE customer_id = 5;

COMMIT;

-- 15. Видалити автора, у якого немає книг
DELETE FROM author
WHERE last_name = 'Забужко';

-- перевірка
SELECT * FROM author;   -- 7 рядків
SELECT * FROM orders;   -- 5 рядків