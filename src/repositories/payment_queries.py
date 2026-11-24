from sqlalchemy import Date, DateTime, cast, func, select

from src.models import Book, OrderItem, Orders, Payment
from src.models.constants import ORDER_CANCELLED, PAYMENT_METHODS, PAYMENT_STATUSES
from src.services.errors import NotFoundError, ValidationError

MAX_PAGE_SIZE = 100


def page_offset(page, page_size):
    if not isinstance(page, int) or page < 1:
        raise ValidationError("Номер сторінки має бути цілим числом від 1")
    if not isinstance(page_size, int) or not 1 <= page_size <= MAX_PAGE_SIZE:
        raise ValidationError(f"Розмір сторінки має бути від 1 до {MAX_PAGE_SIZE}")
    return (page - 1) * page_size


def payments_by_status_and_method(session, status, method, page=1, page_size=10):
    if status not in PAYMENT_STATUSES:
        raise ValidationError(f"Невідомий статус платежу \"{status}\"")
    if method not in PAYMENT_METHODS:
        raise ValidationError(f"Невідомий спосіб оплати \"{method}\"")
    offset = page_offset(page, page_size)
    query = (
        select(Payment)
        .where(Payment.status == status, Payment.method == method)
        .order_by(Payment.date.desc(), Payment.id.desc())
        .limit(page_size)
        .offset(offset)
    )
    return session.scalars(query).all()


def order_items_with_titles(session, order_id):
    if session.get(Orders, order_id) is None:
        raise NotFoundError("Замовлення не знайдено")
    query = (
        select(
            Book.title,
            OrderItem.quantity,
            OrderItem.unit_price,
            (OrderItem.quantity * OrderItem.unit_price).label("line_total"),
        )
        .join(Book, Book.id == OrderItem.book_id)
        .where(OrderItem.order_id == order_id)
        .order_by(Book.title, Book.id)
    )
    return session.execute(query).all()


def monthly_payments_report(session):
    month = func.date_trunc("month", cast(Payment.date, DateTime))
    monthly = (
        select(
            cast(month, Date).label("month"),
            Payment.method.label("method"),
            func.count().label("payments_count"),
            func.sum(Payment.amount).label("total_amount"),
        )
        .join(Orders, Orders.id == Payment.order_id)
        .where(Orders.status != ORDER_CANCELLED)
        .group_by(month, Payment.method)
        .cte("monthly")
    )
    query = (
        select(
            monthly.c.month,
            monthly.c.method,
            monthly.c.payments_count,
            monthly.c.total_amount,
            func.sum(monthly.c.total_amount)
            .over(partition_by=monthly.c.method, order_by=monthly.c.month)
            .label("cumulative_amount"),
            func.rank()
            .over(partition_by=monthly.c.month, order_by=monthly.c.total_amount.desc())
            .label("place"),
        )
        .order_by(monthly.c.month, "place", monthly.c.method)
    )
    return session.execute(query).all()
