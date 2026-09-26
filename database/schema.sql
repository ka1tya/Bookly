CREATE TABLE category (
    category_id SERIAL PRIMARY KEY,
    category_name  VARCHAR(60) NOT NULL UNIQUE
);

CREATE TABLE book (
    book_id SERIAL PRIMARY KEY,
	author_id INT NOT NULL REFERENCES author(author_id),
	title VARCHAR(200) NOT NULL,
	published_year INT CHECK (published_year > 0),
	price NUMERIC(10,2) NOT NULL CHECK (price >= 0)
);

CREATE TABLE book_category (
    fk_book_id INTEGER NOT NULL REFERENCES book(book_id),
	fk_category_id INTEGER NOT NULL REFERENCES category(category_id),
	PRIMARY KEY (fk_book_id, fk_category_id)
);

INSERT INTO category (category_id, category_name) VALUES
    (1, 'Фентезі'),
    (2, 'Детектив'),
    (3, 'Жахи'),
    (4, 'Поезія'),
    (5, 'Наукова фантастика'),
    (6, 'Трилер'),
    (7, 'Романтика');

INSERT INTO book (book_id, author_id, title, published_year, price) VALUES
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
