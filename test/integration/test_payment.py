from decimal import Decimal

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from src.models import OrderItem, Payment
from src.models.constants import ORDER_CANCELLED, ORDER_NEW, ORDER_RECEIVED, ORDER_SHIPPED, PAYMENT_CARD, PAYMENT_CASH, PAYMENT_PAID
from src.services.errors import ConflictError, NotFoundError, OrderStatusError, ValidationError
from src.services.payment_service import add_items_to_order, confirm_cash_payment, remove_order_item

pytestmark = pytest.mark.integration

def count_items(session, order_id):
    return session.scalar(select(func.count()).select_from(OrderItem).where(OrderItem.order_id == order_id))

def count_payments(session, order_id):
    return session.scalar(select(func.count()).select_from(Payment).where(Payment.order_id == order_id))

def test_add_items_creates_payment(session, make_order, make_book):
    order = make_order()
    book1 = make_book(price=Decimal("120.00"))
    book2 = make_book(price=Decimal("80.50"))

    result = add_items_to_order(
        session, order.id,
        [{"book_id": book1.id, "quantity": 2}, {"book_id": book2.id, "quantity": 1}],
        PAYMENT_CARD,
    )

    assert len(result.items) == 2
    assert result.payment.amount == Decimal("320.50")
    assert result.payment.method == PAYMENT_CARD
    assert result.payment.status == "очікує"

def test_unit_price_from_current_book_price(session, make_order, make_book):
    order = make_order()
    book = make_book(price=Decimal("99.99"))

    add_items_to_order(session, order.id, [{"book_id": book.id, "quantity": 1}], PAYMENT_CASH)

    item = session.get(OrderItem, (order.id, book.id))
    assert item.unit_price == Decimal("99.99")

def test_add_items_recalculates_existing_payment(session, make_order, make_book):
    order = make_order()
    book1 = make_book(price=Decimal("100.00"))
    book2 = make_book(price=Decimal("50.00"))
    add_items_to_order(session, order.id, [{"book_id": book1.id, "quantity": 1}], PAYMENT_CARD)

    result = add_items_to_order(session, order.id, [{"book_id": book2.id, "quantity": 2}], PAYMENT_CASH)

    assert count_payments(session, order.id) == 1
    assert result.payment.amount == Decimal("200.00")
    assert result.payment.method == PAYMENT_CASH

def test_add_items_to_paid_payment(session, make_order, make_book, make_payment):
    order = make_order()
    make_payment(order=order, status=PAYMENT_PAID)
    book = make_book()

    session.commit()
    with pytest.raises(ConflictError):
        add_items_to_order(session, order.id, [{"book_id": book.id, "quantity": 1}], PAYMENT_CARD)
    assert count_items(session, order.id) == 0

def test_add_items_invalid_quantity(session, make_order, make_book):
    order = make_order()
    book = make_book()

    session.commit()
    with pytest.raises(ValidationError):
        add_items_to_order(session, order.id, [{"book_id": book.id, "quantity": 11}], PAYMENT_CARD)
    assert count_items(session, order.id) == 0

def test_add_items_not_new_order(session, make_order, make_book):
    order = make_order(status=ORDER_SHIPPED)
    book = make_book()

    session.commit()
    with pytest.raises(OrderStatusError):
        add_items_to_order(session, order.id, [{"book_id": book.id, "quantity": 1}], PAYMENT_CARD)
    assert count_items(session, order.id) == 0
    assert count_payments(session, order.id) == 0

def test_add_items_missing_order(session, make_book):
    book = make_book()

    session.commit()
    with pytest.raises(NotFoundError):
        add_items_to_order(session, 999999, [{"book_id": book.id, "quantity": 1}], PAYMENT_CARD)

def test_add_items_rollback_missing_book(session, make_order, make_book):
    order = make_order()
    order_id = order.id
    book = make_book()

    session.commit()
    with pytest.raises(NotFoundError):
        add_items_to_order(
            session, order_id,
            [{"book_id": book.id, "quantity": 1}, {"book_id": 999999, "quantity": 1}],
            PAYMENT_CARD,
        )
    assert count_items(session, order_id) == 0
    assert count_payments(session, order_id) == 0

def test_add_same_book_twice_rollback(session, make_order, make_book):
    order = make_order()
    order_id = order.id
    book = make_book()

    session.commit()
    with pytest.raises(ConflictError):
        add_items_to_order(
            session, order_id,
            [{"book_id": book.id, "quantity": 1}, {"book_id": book.id, "quantity": 2}],
            PAYMENT_CARD,
        )
    assert count_items(session, order_id) == 0
    assert count_payments(session, order_id) == 0

def test_add_book_already_in_order(session, make_order, make_book, make_order_item):
    order = make_order()
    book = make_book()
    make_order_item(order=order, book=book)

    session.commit()
    with pytest.raises(ConflictError):
        add_items_to_order(session, order.id, [{"book_id": book.id, "quantity": 1}], PAYMENT_CARD)
    assert count_items(session, order.id) == 1

def test_confirm_cash_payment(session, make_order, make_payment):
    order = make_order(status=ORDER_RECEIVED)
    make_payment(order=order, method=PAYMENT_CASH)

    payment = confirm_cash_payment(session, order.id)

    assert payment.status == PAYMENT_PAID

def test_confirm_cash_before_received(session, make_order, make_payment):
    order = make_order(status=ORDER_SHIPPED)
    payment = make_payment(order=order, method=PAYMENT_CASH)

    session.commit()
    with pytest.raises(OrderStatusError):
        confirm_cash_payment(session, order.id)
    assert session.get(Payment, payment.id).status == "очікує"

def test_confirm_card_payment(session, make_order, make_payment):
    order = make_order(status=ORDER_RECEIVED)
    make_payment(order=order, method=PAYMENT_CARD)

    session.commit()
    with pytest.raises(ConflictError):
        confirm_cash_payment(session, order.id)

def test_confirm_already_paid(session, make_order, make_payment):
    order = make_order(status=ORDER_RECEIVED)
    make_payment(order=order, method=PAYMENT_CASH, status=PAYMENT_PAID)

    session.commit()
    with pytest.raises(ConflictError):
        confirm_cash_payment(session, order.id)

def test_confirm_without_payment(session, make_order):
    order = make_order(status=ORDER_RECEIVED)

    session.commit()
    with pytest.raises(NotFoundError):
        confirm_cash_payment(session, order.id)

def test_confirm_missing_order(session):
    session.commit()
    with pytest.raises(NotFoundError):
        confirm_cash_payment(session, 999999)

def test_remove_order_item_recalculates_payment(session, make_order, make_book, make_order_item, make_payment):
    order = make_order()
    book1 = make_book(price=Decimal("100.00"))
    book2 = make_book(price=Decimal("40.00"))
    make_order_item(order=order, book=book1, quantity=1)
    make_order_item(order=order, book=book2, quantity=2)
    payment = make_payment(order=order, amount=Decimal("180.00"))

    remove_order_item(session, order.id, book2.id)

    assert count_items(session, order.id) == 1
    assert session.get(Payment, payment.id).amount == Decimal("100.00")

def test_remove_order_item_without_payment(session, make_order, make_book, make_order_item):
    order = make_order()
    book1 = make_book()
    book2 = make_book()
    make_order_item(order=order, book=book1)
    make_order_item(order=order, book=book2)

    remove_order_item(session, order.id, book1.id)

    assert count_items(session, order.id) == 1

def test_remove_last_item(session, make_order, make_book, make_order_item):
    order = make_order()
    book = make_book()
    make_order_item(order=order, book=book)

    session.commit()
    with pytest.raises(ValidationError):
        remove_order_item(session, order.id, book.id)
    assert count_items(session, order.id) == 1

def test_remove_item_not_new_order(session, make_order, make_book, make_order_item):
    order = make_order(status=ORDER_SHIPPED)
    book1 = make_book()
    book2 = make_book()
    make_order_item(order=order, book=book1)
    make_order_item(order=order, book=book2)

    session.commit()
    with pytest.raises(OrderStatusError):
        remove_order_item(session, order.id, book1.id)
    assert count_items(session, order.id) == 2

def test_remove_missing_item(session, make_order, make_book, make_order_item):
    order = make_order()
    make_order_item(order=order, book=make_book())

    session.commit()
    with pytest.raises(NotFoundError):
        remove_order_item(session, order.id, 999999)

def test_remove_item_missing_order(session):
    session.commit()
    with pytest.raises(NotFoundError):
        remove_order_item(session, 999999, 1)

def set_order_status(session, order_id, status):
    session.execute(text("UPDATE orders SET status = :status WHERE id = :id"), {"status": status, "id": order_id})

def test_confirm_cash_sees_fresh_order_status(session, make_order, make_payment):
    order = make_order(status=ORDER_RECEIVED)
    payment = make_payment(order=order, method=PAYMENT_CASH)
    session.commit()
    set_order_status(session, order.id, ORDER_CANCELLED)

    with pytest.raises(OrderStatusError):
        confirm_cash_payment(session, order.id)
    assert session.get(Payment, payment.id).status == "очікує"

def test_confirm_cash_sees_fresh_payment_status(session, make_order, make_payment):
    order = make_order(status=ORDER_RECEIVED)
    make_payment(order=order, method=PAYMENT_CASH)
    session.commit()
    session.execute(text("UPDATE payment SET status = :status WHERE order_id = :id"), {"status": PAYMENT_PAID, "id": order.id})

    with pytest.raises(ConflictError):
        confirm_cash_payment(session, order.id)

def test_add_items_sees_fresh_order_status(session, make_order, make_book):
    order = make_order()
    book = make_book()
    session.commit()
    set_order_status(session, order.id, ORDER_SHIPPED)

    with pytest.raises(OrderStatusError):
        add_items_to_order(session, order.id, [{"book_id": book.id, "quantity": 1}], PAYMENT_CARD)
    assert count_items(session, order.id) == 0

def test_remove_item_sees_fresh_order_status(session, make_order, make_book, make_order_item):
    order = make_order()
    book1 = make_book()
    book2 = make_book()
    make_order_item(order=order, book=book1)
    make_order_item(order=order, book=book2)
    session.commit()
    set_order_status(session, order.id, ORDER_SHIPPED)

    with pytest.raises(OrderStatusError):
        remove_order_item(session, order.id, book1.id)
    assert count_items(session, order.id) == 2

def test_confirm_cash_lock(engine):
    with engine.connect() as other:
        other.begin()
        other.execute(text("SELECT id FROM orders WHERE id = 3 FOR UPDATE"))

        with Session(engine) as session:
            session.execute(text("SET lock_timeout = '1s'"))
            with pytest.raises(OperationalError):
                confirm_cash_payment(session, order_id=3)

        other.rollback()
