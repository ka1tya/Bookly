import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from src.models import OrderItem, Orders, Payment
from src.models.constants import (
    ORDER_ASSEMBLING, ORDER_CANCELLED, ORDER_NEW, ORDER_RECEIVED, ORDER_SHIPPED,
)
from src.services.errors import NotFoundError, OrderStatusError, ValidationError
from src.services.order_service import change_order_status, delete_cancelled_order

pytestmark = pytest.mark.integration

def count_rows(session, model, order_id):
    return session.scalar(select(func.count()).select_from(model).where(model.order_id == order_id))

def assert_status(engine, order_id, status):
    with Session(engine) as check:
        assert check.get(Orders, order_id).status == status

def test_change_status(session):
    order = change_order_status(session, order_id=4, new_status=ORDER_ASSEMBLING)

    assert order.status == ORDER_ASSEMBLING
    assert session.get(Orders, 4).status == ORDER_ASSEMBLING

def test_full_status_path(session, make_order):
    order = make_order(status=ORDER_NEW)

    for status in [ORDER_ASSEMBLING, ORDER_SHIPPED, ORDER_RECEIVED]:
        order = change_order_status(session, order_id=order.id, new_status=status)

    assert order.status == ORDER_RECEIVED

def test_cancel_assembling_order(session):
    order = change_order_status(session, order_id=3, new_status=ORDER_CANCELLED)
    assert order.status == ORDER_CANCELLED

def test_received_order_cannot_go_back(session):
    with pytest.raises(OrderStatusError):
        change_order_status(session, order_id=1, new_status=ORDER_NEW)
    assert session.get(Orders, 1).status == ORDER_RECEIVED

def test_shipped_order_cannot_be_cancelled(session):
    with pytest.raises(OrderStatusError):
        change_order_status(session, order_id=2, new_status=ORDER_CANCELLED)
    assert session.get(Orders, 2).status == ORDER_SHIPPED

def test_unknown_status(session):
    with pytest.raises(ValidationError):
        change_order_status(session, order_id=4, new_status="втрачено")
    assert session.get(Orders, 4).status == ORDER_NEW

def test_change_status_missing_order(session):
    with pytest.raises(NotFoundError):
        change_order_status(session, order_id=999, new_status=ORDER_ASSEMBLING)

def test_change_status_waits_for_lock(engine):
    with engine.connect() as other:
        other.begin()
        other.execute(text("SELECT id FROM orders WHERE id = 4 FOR UPDATE"))

        with Session(engine) as session:
            session.execute(text("SET lock_timeout = '1s'"))
            with pytest.raises(OperationalError):
                change_order_status(session, order_id=4, new_status=ORDER_ASSEMBLING)

        other.rollback()
    assert_status(engine, 4, ORDER_NEW)

def test_change_status_nowait(engine):
    with engine.connect() as other:
        other.begin()
        other.execute(text("SELECT id FROM orders WHERE id = 4 FOR UPDATE"))

        with Session(engine) as session:
            with pytest.raises(OperationalError):
                change_order_status(session, order_id=4, new_status=ORDER_ASSEMBLING, nowait=True)

        other.rollback()

def test_status_is_reread_after_lock(engine):
    with Session(engine) as session:
        stale_order = session.get(Orders, 4)
        assert stale_order.status == ORDER_NEW

        with engine.begin() as other:
            other.execute(text("UPDATE orders SET status = 'скасовано' WHERE id = 4"))
        try:
            with pytest.raises(OrderStatusError):
                change_order_status(session, order_id=4, new_status=ORDER_ASSEMBLING)
        finally:
            with engine.begin() as other:
                other.execute(text("UPDATE orders SET status = 'нове' WHERE id = 4"))

def test_delete_cancelled_order(session):
    assert count_rows(session, OrderItem, 5) == 1
    assert count_rows(session, Payment, 5) == 1

    delete_cancelled_order(session, order_id=5)

    assert session.get(Orders, 5) is None
    assert count_rows(session, OrderItem, 5) == 0
    assert count_rows(session, Payment, 5) == 0

def test_delete_cancelled_order_without_payment(session, make_order, make_order_item):
    order = make_order(status=ORDER_CANCELLED)
    make_order_item(order=order)
    make_order_item(order=order)

    delete_cancelled_order(session, order_id=order.id)

    assert session.get(Orders, order.id) is None
    assert count_rows(session, OrderItem, order.id) == 0

def test_delete_not_cancelled_order(session):
    with pytest.raises(OrderStatusError):
        delete_cancelled_order(session, order_id=4)
    assert session.get(Orders, 4) is not None
    assert count_rows(session, OrderItem, 4) == 1
    assert count_rows(session, Payment, 4) == 1

def test_delete_missing_order(session):
    with pytest.raises(NotFoundError):
        delete_cancelled_order(session, order_id=999)
