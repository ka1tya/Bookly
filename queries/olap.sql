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