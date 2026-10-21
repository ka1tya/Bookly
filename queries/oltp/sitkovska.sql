-- SELECT

-- 1. Позиції замовлень з назвами книг
SELECT oi.order_id, b.title, oi.quantity, oi.unit_price
FROM order_item oi
JOIN book b ON b.id = oi.book_id
ORDER BY oi.order_id;

-- 2. Позиції, де більше одного примірника
SELECT order_id, book_id, quantity, unit_price
FROM order_item
WHERE quantity > 1;

-- 3. Платежі, що очікують оплати
SELECT id, order_id, amount, method
FROM payment
WHERE status = 'очікує';

-- 4. Платежі карткою понад 300 з іменем клієнта
SELECT p.id, p.order_id, p.amount, c.first_name, c.last_name
FROM payment p
JOIN orders o ON o.id = p.order_id
JOIN customer c ON c.id = o.customer_id
WHERE p.method = 'картка' AND p.amount > 300
ORDER BY p.amount DESC;


-- INSERT

-- Запити 5-7: нове замовлення клієнтки №3 з позиціями та платежем.
-- Виконувати разом, від BEGIN до COMMIT.
BEGIN;

-- 5. Нове замовлення на адресу №4
INSERT INTO orders (customer_id, address_id)
VALUES (3, 4);

-- 6. Позиції замовлення (ціна береться з каталогу)
INSERT INTO order_item (order_id, book_id, quantity, unit_price)
SELECT o.id, b.id, 2, b.price
FROM orders o, book b
WHERE o.id = (SELECT MAX(id) FROM orders WHERE customer_id = 3)
  AND b.title = 'Воно';

INSERT INTO order_item (order_id, book_id, quantity, unit_price)
SELECT o.id, b.id, 1, b.price
FROM orders o, book b
WHERE o.id = (SELECT MAX(id) FROM orders WHERE customer_id = 3)
  AND b.title = 'Кобзар';

-- 7. Платіж за це замовлення
INSERT INTO payment (order_id, amount, method)
SELECT order_id, SUM(quantity * unit_price), 'готівка'
FROM order_item
WHERE order_id = (SELECT MAX(id) FROM orders WHERE customer_id = 3)
GROUP BY order_id;

COMMIT;

-- перевірка
SELECT * FROM order_item
WHERE order_id = (SELECT MAX(id) FROM orders WHERE customer_id = 3);

SELECT * FROM payment
WHERE order_id = (SELECT MAX(id) FROM orders WHERE customer_id = 3);


-- UPDATE

-- Запити 8-9: змінити кількість і перерахувати платіж. Виконувати разом.
BEGIN;

-- 8. Збільшити кількість «Кобзаря» до 3
UPDATE order_item
SET quantity = 3
WHERE order_id = (SELECT MAX(id) FROM orders WHERE customer_id = 3)
  AND book_id = (SELECT id FROM book WHERE title = 'Кобзар');

-- 9. Перерахувати суму платежу
UPDATE payment
SET amount = (SELECT SUM(quantity * unit_price)
              FROM order_item
              WHERE order_id = payment.order_id)
WHERE order_id = (SELECT MAX(id) FROM orders WHERE customer_id = 3);

COMMIT;

-- 10. Позначити платіж як оплачений
UPDATE payment
SET status = 'оплачено'
WHERE order_id = (SELECT MAX(id) FROM orders WHERE customer_id = 3);

-- перевірка
SELECT * FROM payment
WHERE order_id = (SELECT MAX(id) FROM orders WHERE customer_id = 3);


-- DELETE

-- Запити 11-12: видалити позицію і перерахувати платіж. Виконувати разом.
BEGIN;

-- 11. Видалити «Кобзар» із замовлення
DELETE FROM order_item
WHERE order_id = (SELECT MAX(id) FROM orders WHERE customer_id = 3)
  AND book_id = (SELECT id FROM book WHERE title = 'Кобзар');

-- 12. Перерахувати суму платежу
UPDATE payment
SET amount = (SELECT SUM(quantity * unit_price)
              FROM order_item
              WHERE order_id = payment.order_id)
WHERE order_id = (SELECT MAX(id) FROM orders WHERE customer_id = 3);

COMMIT;

-- Запити 13-15: видалення замовлення. Спочатку дочірні таблиці, потім orders
-- (зовнішні ключі без CASCADE). Виконувати разом, від BEGIN до COMMIT.
BEGIN;

-- 13. Видалити платіж замовлення
DELETE FROM payment
WHERE order_id = (SELECT MAX(id) FROM orders WHERE customer_id = 3);

-- 14. Видалити позиції замовлення
DELETE FROM order_item
WHERE order_id = (SELECT MAX(id) FROM orders WHERE customer_id = 3);

-- 15. Видалити саме замовлення
DELETE FROM orders
WHERE id = (SELECT MAX(id) FROM orders WHERE customer_id = 3);

COMMIT;

-- перевірка
SELECT * FROM order_item;   -- 5 рядків
SELECT * FROM payment;      -- 5 рядків
SELECT * FROM orders;       -- 5 рядків