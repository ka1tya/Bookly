-- =====================================================
-- Поліщук Анна — Category, Book, Book_Category
-- =====================================================

-- SELECT
SELECT * FROM category;

SELECT title, price FROM book;

SELECT title, price
FROM book
WHERE price > 300;

-- INSERT
INSERT INTO category (category_name)
VALUES ('Класична проза');

INSERT INTO book (author_id, title, published_year, price)
VALUES (3, 'Зелена миля', 1996, 310.00);

-- UPDATE
UPDATE book
SET price = 330.00
WHERE title = 'Зелена миля';

-- DELETE
DELETE FROM book
WHERE title = 'Зелена миля';

-- Варенко Катерина — Customer, Address
-- SELECT
SELECT * FROM customer
WHERE email LIKE '%sofia%';
 
SELECT a.city, a.street, a.postal_code
FROM address a
JOIN customer c ON c.id = a.customer_id
WHERE c.email = 'diva@gmail.com';
 
SELECT c.first_name, c.last_name, a.city
FROM customer c
JOIN address a ON a.customer_id = c.id
WHERE a.city = 'Київ'
ORDER BY c.last_name;
 
-- INSERT
INSERT INTO customer (first_name, last_name, email, phone)
VALUES ('Анастасія', 'Бойко', 'uwu111@gmail.com', '+380661234567');
 
INSERT INTO address (customer_id, country, city, street, postal_code)
SELECT id, 'Україна', 'Житомир', 'вул. Рибальська 5В', '14451'
FROM customer
WHERE email = 'uwu111@gmail.com';

-- UPDATE
UPDATE customer
SET phone = '+380982361534'
WHERE email = 'uwu111@gmail.com';
 
UPDATE address
SET postal_code = '88413'
WHERE customer_id = (SELECT id FROM customer WHERE email = 'uwu111@gmail.com');
 
-- DELETE
DELETE FROM address
WHERE customer_id = (SELECT id FROM customer WHERE email = 'uwu111@gmail.com');
 
DELETE FROM customer
WHERE email = 'uwu111@gmail.com';