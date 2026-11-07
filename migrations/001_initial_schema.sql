-- 001: створення таблиць Bookly (PostgreSQL 16)

CREATE TABLE author (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL
);

CREATE TABLE customer (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE category (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_name VARCHAR(60) NOT NULL UNIQUE
);

CREATE TABLE address (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id INT NOT NULL,
    country VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    street VARCHAR(255) NOT NULL,
    postal_code VARCHAR(20),
    FOREIGN KEY (customer_id) REFERENCES customer(id) ON DELETE CASCADE
);

CREATE TABLE book (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    author_id INTEGER NOT NULL REFERENCES author(id),
    title VARCHAR(200) NOT NULL,
    published_year INTEGER CHECK (published_year > 0),
    price NUMERIC(10,2) NOT NULL CHECK (price >= 0)
);

CREATE TABLE book_category (
    book_id INTEGER NOT NULL REFERENCES book(id),
    category_id INTEGER NOT NULL REFERENCES category(id),
    PRIMARY KEY (book_id, category_id)
);

CREATE TABLE orders (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customer(id) ON DELETE RESTRICT,
    address_id INTEGER NOT NULL REFERENCES address(id) ON DELETE RESTRICT,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'нове'
        CHECK (status IN ('нове', 'збирається', 'відправлено', 'отримано', 'скасовано'))
);

CREATE TABLE order_item (
    order_id INTEGER NOT NULL REFERENCES orders(id),
    book_id INTEGER NOT NULL REFERENCES book(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0 AND quantity <= 10),
    unit_price NUMERIC(10,2) NOT NULL CHECK (unit_price >= 0),
    PRIMARY KEY (order_id, book_id)
);

CREATE TABLE payment (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id INTEGER NOT NULL UNIQUE REFERENCES orders(id),
    amount NUMERIC(10,2) NOT NULL CHECK (amount >= 0),
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    method VARCHAR(20) NOT NULL CHECK (method IN ('картка', 'готівка')),
    status VARCHAR(20) NOT NULL DEFAULT 'очікує' CHECK (status IN ('очікує', 'оплачено'))
);
