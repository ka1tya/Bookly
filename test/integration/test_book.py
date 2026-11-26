from decimal import Decimal

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from src.models import Book, Category, OrderItem, book_category
from src.services.book_errors import BookInOrdersError
from src.services.book_service import (
    change_book_price,
    create_book_with_categories,
    delete_book_not_in_orders,
    get_current_prices,
)
from src.services.errors import ConflictError, LockedError, NotFoundError, ValidationError

pytestmark = pytest.mark.integration

BOOK_ID = 3


def count_books(session):
    return session.scalar(select(func.count()).select_from(Book))


def count_links(session):
    return session.scalar(select(func.count()).select_from(book_category))


def categories_of(session, book_id):
    query = select(book_category.c.category_id).where(book_category.c.book_id == book_id)
    return sorted(session.scalars(query))


def price_of(session, book_id):
    return session.scalar(select(Book.price).where(Book.id == book_id))


def lock_row(conn, book_id):
    conn.execute(text("SELECT id FROM book WHERE id = :id FOR UPDATE"), {"id": book_id})


@pytest.fixture
def own_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


def test_create_book(session):
    book = create_book_with_categories(session, 4, "  Інкрустації  ", 1994, "150.00", [4, 7])

    assert book.id is not None
    assert book.title == "Інкрустації"
    assert book.price == Decimal("150.00")
    assert book.author.last_name == "Костенко"
    assert sorted(c.category_name for c in book.categories) == ["Поезія", "Романтика"]
    assert categories_of(session, book.id) == [4, 7]


def test_create_book_no_author(session):
    before = count_books(session)
    with pytest.raises(NotFoundError):
        create_book_with_categories(session, 999, "Книга", 2020, 100, [1])
    assert count_books(session) == before


def test_create_book_rollback(session):
    books, links = count_books(session), count_links(session)
    with pytest.raises(NotFoundError):
        create_book_with_categories(session, 1, "Відкат", 2020, 100, [1, 999])

    assert count_books(session) == books
    assert count_links(session) == links
    assert session.scalar(select(Book).where(Book.title == "Відкат")) is None


def test_create_book_same_category(session):
    before = count_books(session)
    with pytest.raises(ValidationError):
        create_book_with_categories(session, 1, "Книга", 2020, 100, [1, 1])
    assert count_books(session) == before


def test_create_book_bad_data(session):
    before = count_books(session)
    with pytest.raises(ValidationError):
        create_book_with_categories(session, 1, "", 2020, 100, [1])
    with pytest.raises(ValidationError):
        create_book_with_categories(session, 1, "Книга", 2020, -1, [1])
    assert count_books(session) == before


def test_change_price(session):
    book = change_book_price(session, BOOK_ID, "500.00")

    assert book.price == Decimal("500.00")
    assert price_of(session, BOOK_ID) == Decimal("500.00")


def test_order_price_not_changed(session):
    change_book_price(session, 1, "400.00")

    unit_price = session.scalar(
        select(OrderItem.unit_price).where(OrderItem.order_id == 1, OrderItem.book_id == 1)
    )
    assert price_of(session, 1) == Decimal("400.00")
    assert unit_price == Decimal("350.00")


@pytest.mark.parametrize("new_price", ["420.00", "0", "-5", "631.00", "209.99"])
def test_change_price_wrong(session, new_price):
    with pytest.raises(ValidationError):
        change_book_price(session, BOOK_ID, new_price)
    assert price_of(session, BOOK_ID) == Decimal("420.00")


def test_change_price_uses_fresh_price(session):
    session.get(Book, BOOK_ID)
    session.execute(text("UPDATE book SET price = 300 WHERE id = :id"), {"id": BOOK_ID})

    with pytest.raises(ValidationError):
        change_book_price(session, BOOK_ID, "500.00")


def test_change_price_no_book(session):
    with pytest.raises(NotFoundError):
        change_book_price(session, 999, "100.00")


def test_change_price_nowait(engine, own_session):
    with engine.connect() as other:
        other.begin()
        lock_row(other, BOOK_ID)

        with pytest.raises(LockedError):
            change_book_price(own_session, BOOK_ID, "500.00", nowait=True)

        other.rollback()
    assert price_of(own_session, BOOK_ID) == Decimal("420.00")


def test_change_price_timeout(engine, own_session):
    with engine.connect() as other:
        other.begin()
        lock_row(other, BOOK_ID)

        own_session.execute(text("SET LOCAL lock_timeout = '500ms'"))
        with pytest.raises(LockedError):
            change_book_price(own_session, BOOK_ID, "500.00")

        other.rollback()


def test_delete_book(session):
    delete_book_not_in_orders(session, BOOK_ID)

    assert session.get(Book, BOOK_ID) is None
    assert categories_of(session, BOOK_ID) == []
    assert session.get(Category, 3) is not None


def test_delete_book_in_orders(session):
    with pytest.raises(BookInOrdersError):
        delete_book_not_in_orders(session, 1)

    assert session.get(Book, 1) is not None
    assert categories_of(session, 1) == [1]


def test_delete_no_book(session):
    with pytest.raises(NotFoundError):
        delete_book_not_in_orders(session, 999)


def test_delete_new_book(session):
    book = create_book_with_categories(session, 2, "Колискова", 2002, 250, [2, 6])
    delete_book_not_in_orders(session, book.id)

    assert session.get(Book, book.id) is None
    assert categories_of(session, book.id) == []


def test_current_prices(session):
    assert get_current_prices(session, [1, 5, 5]) == {1: Decimal("350.00"), 5: Decimal("180.00")}


def test_current_prices_empty(session):
    assert get_current_prices(session, []) == {}


def test_current_prices_no_book(session):
    with pytest.raises(NotFoundError, match="999"):
        get_current_prices(session, [1, 999])


def test_current_prices_no_commit(session, make_book):
    book = make_book(price=Decimal("75.00"))
    assert get_current_prices(session, [book.id]) == {book.id: Decimal("75.00")}
    session.rollback()
    assert session.get(Book, book.id) is None


def test_create_book_other_db_error(session, monkeypatch):
    import src.services.book_service as book_service

    def broken_categories(session, book_id, category_ids):
        raise IntegrityError("INSERT", {}, Exception("інша помилка БД"))

    monkeypatch.setattr(book_service, "add_categories", broken_categories)

    before = count_books(session)
    with pytest.raises(ConflictError):
        create_book_with_categories(session, 1, "Книга", 2020, 100, [1])
    assert count_books(session) == before


def test_change_price_other_db_error(session, monkeypatch):
    import src.services.book_service as book_service

    def broken_lock(session, book_id, nowait=False):
        raise OperationalError("SELECT", {}, Exception("з'єднання втрачено"))

    monkeypatch.setattr(book_service, "lock_book", broken_lock)

    with pytest.raises(OperationalError):
        change_book_price(session, BOOK_ID, "500.00")
    assert price_of(session, BOOK_ID) == Decimal("420.00")


def test_delete_book_db_error(session, monkeypatch):
    import src.services.book_service as book_service

    def broken_in_orders(session, book_id):
        raise IntegrityError("DELETE", {}, Exception("порушення зв'язку"))

    monkeypatch.setattr(book_service, "in_orders", broken_in_orders)

    before = count_books(session)
    with pytest.raises(BookInOrdersError):
        delete_book_not_in_orders(session, BOOK_ID)
    assert count_books(session) == before