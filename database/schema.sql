CREATE TABLE author (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL
);

INSERT INTO author (id, first_name, last_name) VALUES
    (1, 'Джоан', 'Роулінг'),
    (2, 'Чак', 'Поланік'),
    (3, 'Стівен', 'Кінг'),
    (4, 'Ліна', 'Костенко'),
    (5, 'Тарас', 'Шевченко'),
    (6, 'Агата', 'Крісті'),
    (7, 'Г. Д.', 'Карлтон');

SELECT setval('author_id_seq', (SELECT MAX(id) FROM author));

CREATE TABLE customer (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE category (
    category_id SERIAL PRIMARY KEY,
    category_name  VARCHAR(60) NOT NULL UNIQUE
);

CREATE TABLE address (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    country VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    street VARCHAR(255) NOT NULL,
    postal_code VARCHAR(20),
	FOREIGN KEY (customer_id) REFERENCES customer(id) ON DELETE CASCADE
);

CREATE TABLE book (
    book_id SERIAL PRIMARY KEY,
	fk_author_id INT NOT NULL REFERENCES author(author(id)),
	title VARCHAR(200) NOT NULL,
	published_year INT CHECK (published_year > 0),
	price NUMERIC(10,2) NOT NULL CHECK (price >= 0)
);

CREATE TABLE book_category (
    fk_book_id INTEGER NOT NULL REFERENCES book(book_id),
	fk_category_id INTEGER NOT NULL REFERENCES category(category_id),
	PRIMARY KEY (fk_book_id, fk_category_id)
);

CREATE INDEX idx_address_customer_id ON address(customer_id);

INSERT INTO category (category_id, category_name) VALUES
    (1, 'Фентезі'),
    (2, 'Детектив'),
    (3, 'Жахи'),
    (4, 'Поезія'),
    (5, 'Наукова фантастика'),
    (6, 'Трилер'),
    (7, 'Романтика');

INSERT INTO book (book_id, fk_author_id, title, published_year, price) VALUES
    (1, 1, 'Гаррі Поттер і філософський камінь', 1997, 350.00),
    (2, 2, 'Бійцівський клуб', 1996, 300.00),
    (3, 3, 'Воно', 1986, 420.00),
    (4, 4, 'Маруся Чурай', 1979, 200.00),
    (5, 5, 'Кобзар', 1840, 180.00),
    (6, 6, 'Вбивство у Східному експресі', 1934, 260.00),
    (7, 7, 'Переслідування Аделіни', 2021, 430.00);

INSERT INTO book_category (fk_book_id, fk_category_id) VALUES
    (1, 1),
    (2, 6),
    (3, 3),
    (3, 6),
    (4, 4),
    (5, 4),
    (6, 2),
    (7, 6),
    (7, 7);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customer(id) ON DELETE RESTRICT,
    address_id INTEGER NOT NULL REFERENCES address(id) ON DELETE RESTRICT,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'нове'
        CHECK (status IN ('нове', 'збирається', 'відправлено', 'отримано', 'скасовано'))
);

CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_address_id ON orders(address_id);

--тимчасові дані для таблиць customer, address та orders
/*
INSERT INTO customer (id, first_name, last_name, email, phone) VALUES
    (1, 'Олена', 'Іваненко', 'diva@gmail.com', '+380501111111'),
    (2, 'Софія', 'Ковальчук', 'sofia@gmail.com', '+380502222222'),
    (3, 'Максим', 'Петренко', 'max@gmail.com', '+380503333333'),
    (4, 'Джон', 'Сміт', 'john@gmail.com', '+380504444444');

INSERT INTO address (id, customer_id, country, city, street, postal_code) VALUES
    (1, 1, 'Україна', 'Київ', 'вул. Хрещатик 1', '01001'),
    (2, 1, 'Україна', 'Київ', 'вул. Саксаганського 10', '01033'),
    (3, 2, 'Україна', 'Одеса', 'вул. Дерибасівська 5', '65000'),
    (4, 3, 'Україна', 'Харків', 'вул. Сумська 20', '61000'),
    (5, 4, 'США', 'Нью-Йорк', '5th Avenue 100', '10001');
*/

INSERT INTO orders (id, customer_id, address_id, date, status) VALUES
    (1, 1, 1, '2025-09-01', 'отримано'),
    (2, 1, 2, '2025-09-15', 'відправлено'),
    (3, 2, 3, '2025-09-20', 'збирається'),
    (4, 3, 4, '2025-10-01', 'нове'),
    (5, 4, 5, '2025-10-03', 'скасовано');

SELECT setval('orders_id_seq', (SELECT MAX(id) FROM orders));