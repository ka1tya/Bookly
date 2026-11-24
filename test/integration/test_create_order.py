from decimal import Decimal

import pytest
from sqlalchemy import func, select
from src.models import Book, OrderItem, Orders, Payment
from src.models.constants import ORDER_NEW, PAYMENT_CASH, PAYMENT_CARD, PAYMENT_PENDING
from src.services.errors import ConflictError, NotFoundError, ValidationError
from src.services.order_service import create_order

pytestmark = pytest.mark.integration

def count(session, model):
    return session.scalar(select(func.count()).select_from(model))

def assert_nothing_created(session, orders, items, payments):
    assert count(session, Orders) == orders
    assert count(session, OrderItem) == items
    assert count(session, Payment) == payments

def test_create_order(session):
    order = create_order(session, customer_id=1, address_id=1,
                         items=[{"book_id": 1, "quantity": 2}, {"book_id": 5, "quantity": 1}],
                         payment_method=PAYMENT_CARD)

    assert order.id is not None
    assert order.status == ORDER_NEW
    assert order.customer_id == 1
    assert order.address_id == 1
    assert {(item.book_id, item.quantity) for item in order.items} == {(1, 2), (5, 1)}
    assert order.payment.amount == Decimal("880.00")
    assert order.payment.method == PAYMENT_CARD
    assert order.payment.status == PAYMENT_PENDING

def test_payment_equals_items_total(session):
    order = create_order(session, customer_id=3, address_id=4,
                         items=[{"book_id": 3, "quantity": 1}, {"book_id": 7, "quantity": 3}],
                         payment_method=PAYMENT_CASH)

    total = sum(item.quantity * item.unit_price for item in order.items)
    assert order.payment.amount == total == Decimal("1710.00")

def test_unit_price_is_current_price(session):
    session.get(Book, 2).price = Decimal("315.00")
    session.flush()

    order = create_order(session, customer_id=1, address_id=2,
                         items=[{"book_id": 2, "quantity": 1}], payment_method=PAYMENT_CARD)

    assert order.items[0].unit_price == Decimal("315.00")

def test_old_orders_keep_their_price(session):
    session.get(Book, 1).price = Decimal("999.00")
    session.flush()

    create_order(session, customer_id=1, address_id=1, items=[{"book_id": 1, "quantity": 1}], payment_method=PAYMENT_CARD)

    assert session.get(OrderItem, (1, 1)).unit_price == Decimal("350.00")

def test_other_customer_address(session):
    with pytest.raises(ConflictError):
        create_order(session, customer_id=1, address_id=3,
                     items=[{"book_id": 1, "quantity": 1}], payment_method=PAYMENT_CARD)
    assert_nothing_created(session, 5, 5, 5)

def test_missing_customer(session):
    with pytest.raises(NotFoundError):
        create_order(session, customer_id=999, address_id=1,
                     items=[{"book_id": 1, "quantity": 1}], payment_method=PAYMENT_CARD)
    assert_nothing_created(session, 5, 5, 5)

def test_missing_address(session):
    with pytest.raises(NotFoundError):
        create_order(session, customer_id=1, address_id=999,
                     items=[{"book_id": 1, "quantity": 1}], payment_method=PAYMENT_CARD)
    assert_nothing_created(session, 5, 5, 5)

def test_missing_book_rolls_back_everything(session):
    with pytest.raises(NotFoundError):
        create_order(session, customer_id=1, address_id=1,
                     items=[{"book_id": 1, "quantity": 1}, {"book_id": 999, "quantity": 1}],
                     payment_method=PAYMENT_CARD)
    assert_nothing_created(session, 5, 5, 5)

def test_quantity_eleven(session):
    with pytest.raises(ValidationError):
        create_order(session, customer_id=1, address_id=1,
                     items=[{"book_id": 1, "quantity": 11}], payment_method=PAYMENT_CARD)
    assert_nothing_created(session, 5, 5, 5)

def test_empty_items(session):
    with pytest.raises(ValidationError):
        create_order(session, customer_id=1, address_id=1, items=[], payment_method=PAYMENT_CARD)
    assert_nothing_created(session, 5, 5, 5)

def test_wrong_payment_method(session):
    with pytest.raises(ValidationError):
        create_order(session, customer_id=1, address_id=1,
                     items=[{"book_id": 1, "quantity": 1}], payment_method="біткоїн")
    assert_nothing_created(session, 5, 5, 5)

def test_rollback_after_db_error(session, monkeypatch):
    import src.services.order_service as order_service

    def broken_payment(session, order, method):
        raise RuntimeError("збій під час створення платежу")

    monkeypatch.setattr(order_service, "create_pending_payment", broken_payment)

    with pytest.raises(RuntimeError):
        create_order(session, customer_id=1, address_id=1,
                     items=[{"book_id": 1, "quantity": 1}], payment_method=PAYMENT_CARD)
    assert_nothing_created(session, 5, 5, 5)
