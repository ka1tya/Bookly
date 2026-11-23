import datetime
from decimal import Decimal

import pytest

from src.models.constants import ORDER_CANCELLED, PAYMENT_CARD, PAYMENT_CASH, PAYMENT_PAID, PAYMENT_PENDING
from src.repositories.payment_queries import monthly_payments_report, order_items_with_titles, payments_by_status_and_method
from src.services.errors import NotFoundError, ValidationError

pytestmark = pytest.mark.integration


def ids(payments):
    return [payment.id for payment in payments]


def report_rows(session):
    return [
        (row.month, row.method, row.payments_count, row.total_amount, row.cumulative_amount, row.place)
        for row in monthly_payments_report(session)
    ]


def test_payments_filter_by_both_conditions(session):
    assert ids(payments_by_status_and_method(session, PAYMENT_PENDING, PAYMENT_CASH)) == [4, 2]


def test_payments_paid_card(session):
    assert ids(payments_by_status_and_method(session, PAYMENT_PAID, PAYMENT_CARD)) == [1]


def test_payments_pending_card(session):
    assert ids(payments_by_status_and_method(session, PAYMENT_PENDING, PAYMENT_CARD)) == [5, 3]


def test_payments_nothing_found(session):
    assert payments_by_status_and_method(session, PAYMENT_PAID, PAYMENT_CASH) == []


def test_payments_newest_first(session, make_payment):
    newest = make_payment(method=PAYMENT_CASH, status=PAYMENT_PENDING, date=datetime.date(2030, 1, 1))

    assert ids(payments_by_status_and_method(session, PAYMENT_PENDING, PAYMENT_CASH))[0] == newest.id


def test_payments_same_date_by_id_desc(session, make_payment):
    first = make_payment(method=PAYMENT_CASH, date=datetime.date(2030, 1, 1))
    second = make_payment(method=PAYMENT_CASH, date=datetime.date(2030, 1, 1))

    assert ids(payments_by_status_and_method(session, PAYMENT_PENDING, PAYMENT_CASH))[:2] == [second.id, first.id]


def test_payments_pages(session):
    first = payments_by_status_and_method(session, PAYMENT_PENDING, PAYMENT_CARD, page=1, page_size=1)
    second = payments_by_status_and_method(session, PAYMENT_PENDING, PAYMENT_CARD, page=2, page_size=1)
    third = payments_by_status_and_method(session, PAYMENT_PENDING, PAYMENT_CARD, page=3, page_size=1)

    assert ids(first) == [5]
    assert ids(second) == [3]
    assert third == []


def test_payments_wrong_status(session):
    with pytest.raises(ValidationError):
        payments_by_status_and_method(session, "невідомо", PAYMENT_CARD)


def test_payments_wrong_method(session):
    with pytest.raises(ValidationError):
        payments_by_status_and_method(session, PAYMENT_PENDING, "біткоїн")


def test_payments_wrong_page(session):
    with pytest.raises(ValidationError):
        payments_by_status_and_method(session, PAYMENT_PENDING, PAYMENT_CARD, page=0)


def test_order_items_demo_order(session):
    rows = order_items_with_titles(session, 2)

    assert [(row.title, row.quantity, row.unit_price, row.line_total) for row in rows] == [
        ("Бійцівський клуб", 2, Decimal("300.00"), Decimal("600.00")),
    ]


def test_order_items_sorted_by_title(session, make_order, make_book, make_order_item):
    order = make_order()
    make_order_item(order=order, book=make_book(title="Яблуко"), quantity=1, unit_price=Decimal("10.00"))
    make_order_item(order=order, book=make_book(title="Абетка"), quantity=3, unit_price=Decimal("20.50"))

    rows = order_items_with_titles(session, order.id)

    assert [row.title for row in rows] == ["Абетка", "Яблуко"]
    assert [row.line_total for row in rows] == [Decimal("61.50"), Decimal("10.00")]


def test_order_items_uses_price_from_order_not_book(session, make_order, make_book, make_order_item):
    order = make_order()
    book = make_book(price=Decimal("500.00"))
    make_order_item(order=order, book=book, quantity=2, unit_price=Decimal("100.00"))

    rows = order_items_with_titles(session, order.id)

    assert rows[0].unit_price == Decimal("100.00")
    assert rows[0].line_total == Decimal("200.00")


def test_order_items_empty_order(session, make_order):
    assert order_items_with_titles(session, make_order().id) == []


def test_order_items_missing_order(session):
    with pytest.raises(NotFoundError):
        order_items_with_titles(session, 999999)


def test_report_demo_data(session):
    assert report_rows(session) == [
        (datetime.date(2025, 9, 1), PAYMENT_CASH, 1, Decimal("600.00"), Decimal("600.00"), 1),
        (datetime.date(2025, 9, 1), PAYMENT_CARD, 2, Decimal("550.00"), Decimal("550.00"), 2),
        (datetime.date(2025, 10, 1), PAYMENT_CASH, 1, Decimal("260.00"), Decimal("860.00"), 1),
    ]


def test_report_skips_cancelled_orders(session):
    methods_in_october = [row[1] for row in report_rows(session) if row[0] == datetime.date(2025, 10, 1)]

    assert methods_in_october == [PAYMENT_CASH]


def test_report_cumulative_sum_per_method(session, make_order, make_payment):
    make_payment(order=make_order(), method=PAYMENT_CARD, amount=Decimal("100.00"), date=datetime.date(2030, 1, 15))
    make_payment(order=make_order(), method=PAYMENT_CARD, amount=Decimal("50.00"), date=datetime.date(2030, 2, 3))
    make_payment(order=make_order(), method=PAYMENT_CARD, amount=Decimal("25.00"), date=datetime.date(2030, 2, 20))

    card_rows = [row for row in report_rows(session) if row[1] == PAYMENT_CARD and row[0].year == 2030]

    assert [(row[0], row[2], row[3], row[4]) for row in card_rows] == [
        (datetime.date(2030, 1, 1), 1, Decimal("100.00"), Decimal("650.00")),
        (datetime.date(2030, 2, 1), 2, Decimal("75.00"), Decimal("725.00")),
    ]


def test_report_ranks_methods_within_month(session, make_order, make_payment):
    make_payment(order=make_order(), method=PAYMENT_CARD, amount=Decimal("300.00"), date=datetime.date(2030, 3, 5))
    make_payment(order=make_order(), method=PAYMENT_CASH, amount=Decimal("100.00"), date=datetime.date(2030, 3, 6))

    march = [(row[1], row[5]) for row in report_rows(session) if row[0] == datetime.date(2030, 3, 1)]

    assert march == [(PAYMENT_CARD, 1), (PAYMENT_CASH, 2)]


def test_report_equal_totals_share_place(session, make_order, make_payment):
    make_payment(order=make_order(), method=PAYMENT_CARD, amount=Decimal("100.00"), date=datetime.date(2030, 4, 5))
    make_payment(order=make_order(), method=PAYMENT_CASH, amount=Decimal("100.00"), date=datetime.date(2030, 4, 6))

    april = [row[5] for row in report_rows(session) if row[0] == datetime.date(2030, 4, 1)]

    assert april == [1, 1]


def test_report_new_cancelled_order_is_ignored(session, make_order, make_payment):
    cancelled = make_order(status=ORDER_CANCELLED)
    make_payment(order=cancelled, method=PAYMENT_CARD, amount=Decimal("999.00"), date=datetime.date(2030, 5, 5))

    assert [row for row in report_rows(session) if row[0] == datetime.date(2030, 5, 1)] == []
