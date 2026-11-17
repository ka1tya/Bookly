from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from src.models.constants import ORDER_RECEIVED, PAYMENT_CASH

pytestmark = pytest.mark.integration


def test_factories_build_full_order(session, make_order, make_order_item, make_book, make_payment):
    order = make_order(status=ORDER_RECEIVED)
    book = make_book(price=Decimal("250.00"))
    item = make_order_item(order=order, book=book, quantity=2)
    payment = make_payment(order=order, amount=Decimal("500.00"), method=PAYMENT_CASH)

    assert order.status == ORDER_RECEIVED
    assert item.unit_price == Decimal("250.00")
    assert payment.order_id == order.id
    assert payment.status == "очікує"


def test_quantity_out_of_range(session, make_order_item):
    with pytest.raises(IntegrityError):
        make_order_item(quantity=11)


def test_second_payment_for_order_rejected(session, make_order, make_payment):
    order = make_order()
    make_payment(order=order)
    with pytest.raises(IntegrityError):
        make_payment(order=order)


def test_factory_data_is_rolled_back(session, make_customer):
    from src.models import Customer
    make_customer(email="rollback-check@test.com")
    session.rollback()
    assert session.query(Customer).filter_by(email="rollback-check@test.com").count() == 0
