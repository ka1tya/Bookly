from decimal import Decimal

import pytest
from src.models import Orders, Payment
from src.models.constants import ORDER_CANCELLED, ORDER_NEW, ORDER_RECEIVED, PAYMENT_CASH, PAYMENT_PAID
from src.repositories.order_repository import customer_orders, orders_audit, search_authors

pytestmark = pytest.mark.integration

def last_names(authors):
    return [author.last_name for author in authors]

def test_search_authors_by_last_name(session):
    assert last_names(search_authors(session, "Кінг")) == ["Кінг"]

def test_search_authors_any_case(session):
    assert last_names(search_authors(session, "кінг")) == ["Кінг"]

def test_search_authors_by_first_name(session):
    assert last_names(search_authors(session, "Тарас")) == ["Шевченко"]

def test_search_authors_by_part(session):
    # "ен" є у прізвищах Костенко і Шевченко та в імені Стівен (Кінг)
    assert set(last_names(search_authors(session, "ен"))) == {"Костенко", "Шевченко", "Кінг"}

def test_search_authors_pages(session):
    first = search_authors(session, "к", page=1, page_size=2)
    second = search_authors(session, "к", page=2, page_size=2)
    everything = search_authors(session, "к", page=1, page_size=100)

    assert len(first) == 2
    assert last_names(first + second) == last_names(everything)[:len(first) + len(second)]
    assert not set(last_names(first)) & set(last_names(second))

def test_search_authors_not_found(session):
    assert search_authors(session, "Толкін") == []

def test_customer_orders(session):
    rows = customer_orders(session, customer_id=1)
    assert [row.id for row in rows] == [2, 1]
    assert {row.city for row in rows} == {"Київ"}

def test_customer_orders_by_status(session):
    rows = customer_orders(session, customer_id=1, status=ORDER_RECEIVED)
    assert [(row.id, row.street) for row in rows] == [(1, "вул. Борщагівська 14")]

def test_customer_orders_second_page(session):
    rows = customer_orders(session, customer_id=1, page=2, page_size=1)
    assert [row.id for row in rows] == [1]

def test_customer_without_orders(session):
    assert customer_orders(session, customer_id=5) == []

def test_audit_demo_data_is_clean(session):
    assert orders_audit(session) == []

def test_audit_finds_empty_order_without_payment(session, make_order):
    order = make_order(status=ORDER_NEW)

    rows = orders_audit(session)

    assert [row.order_id for row in rows] == [order.id]
    assert rows[0].empty_order
    assert rows[0].no_payment
    assert rows[0].items_count == 0

def test_audit_finds_amount_mismatch(session):
    session.get(Payment, 3).amount = Decimal("999.00")
    session.flush()

    rows = orders_audit(session)

    assert [row.order_id for row in rows] == [3]
    assert rows[0].amount_mismatch
    assert rows[0].items_total == Decimal("200.00")
    assert not rows[0].empty_order

def test_audit_finds_cash_paid_before_received(session):
    payment = session.get(Payment, 2)
    assert payment.method == PAYMENT_CASH
    payment.status = PAYMENT_PAID
    session.flush()

    rows = orders_audit(session)

    assert [row.order_id for row in rows] == [2]
    assert rows[0].cash_paid_early
    assert not rows[0].amount_mismatch

def test_audit_cash_paid_after_received_is_ok(session):
    session.get(Orders, 2).status = ORDER_RECEIVED
    session.get(Payment, 2).status = PAYMENT_PAID
    session.flush()

    assert orders_audit(session) == []

def test_audit_cancelled_order_is_checked_too(session, make_order, make_order_item):
    order = make_order(status=ORDER_CANCELLED)
    make_order_item(order=order)

    rows = orders_audit(session)

    assert [row.order_id for row in rows] == [order.id]
    assert rows[0].no_payment
    assert not rows[0].empty_order
