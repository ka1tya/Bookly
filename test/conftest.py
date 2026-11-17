import itertools
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.db import TEST_DATABASE_URL
from src.models import Address, Author, Book, Customer, OrderItem, Orders, Payment
from src.models.constants import ORDER_NEW, PAYMENT_CARD, PAYMENT_PENDING

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(TEST_DATABASE_URL)
    yield engine
    engine.dispose()

@pytest.fixture
def session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

_counter = itertools.count(1)


def _n():
    return next(_counter)


@pytest.fixture
def make_customer(session):
    def factory(**kw):
        n = _n()
        data = dict(
            first_name="Тест",
            last_name=f"Клієнт{n}",
            email=f"factory{n}@test.com",
            phone=f"+38099{n:07d}",
        )
        data.update(kw)
        obj = Customer(**data)
        session.add(obj)
        session.flush()
        return obj
    return factory


@pytest.fixture
def make_address(session, make_customer):
    def factory(customer=None, **kw):
        customer = customer or make_customer()
        data = dict(
            customer_id=customer.id,
            country="Україна",
            city="Київ",
            street=f"вул. Тестова {_n()}",
            postal_code="01001",
        )
        data.update(kw)
        obj = Address(**data)
        session.add(obj)
        session.flush()
        return obj
    return factory


@pytest.fixture
def make_book(session):
    def factory(**kw):
        n = _n()
        if "author_id" not in kw:
            author = Author(first_name="Тест", last_name=f"Автор{n}")
            session.add(author)
            session.flush()
            kw["author_id"] = author.id
        data = dict(title=f"Книга {n}", published_year=2020, price=Decimal("100.00"))
        data.update(kw)
        obj = Book(**data)
        session.add(obj)
        session.flush()
        return obj
    return factory


@pytest.fixture
def make_order(session, make_address):
    def factory(status=ORDER_NEW, address=None, **kw):
        address = address or make_address()
        data = dict(customer_id=address.customer_id, address_id=address.id, status=status)
        data.update(kw)
        obj = Orders(**data)
        session.add(obj)
        session.flush()
        return obj
    return factory


@pytest.fixture
def make_order_item(session, make_order, make_book):
    def factory(order=None, book=None, quantity=1, unit_price=None, **kw):
        order = order or make_order()
        book = book or make_book()
        data = dict(
            order_id=order.id,
            book_id=book.id,
            quantity=quantity,
            unit_price=unit_price if unit_price is not None else book.price,
        )
        data.update(kw)
        obj = OrderItem(**data)
        session.add(obj)
        session.flush()
        return obj
    return factory


@pytest.fixture
def make_payment(session, make_order):
    def factory(order=None, amount=Decimal("100.00"), method=PAYMENT_CARD, status=PAYMENT_PENDING, **kw):
        order = order or make_order()
        data = dict(order_id=order.id, amount=amount, method=method, status=status)
        data.update(kw)
        obj = Payment(**data)
        session.add(obj)
        session.flush()
        return obj
    return factory
