-- 002: індекси для зовнішніх ключів і частих фільтрів
-- customer.email і customer.phone мають UNIQUE, тому індекс для них уже створено автоматично.

CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_address_id ON orders(address_id);
CREATE INDEX idx_address_customer_id ON address(customer_id);
CREATE INDEX idx_address_city ON address(city);
CREATE INDEX idx_book_author_id ON book(author_id);
