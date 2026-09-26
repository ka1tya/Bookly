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