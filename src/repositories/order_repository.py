from sqlalchemy import and_, case, func, or_, select
from src.models import Address, Author, OrderItem, Orders, Payment
from src.models.constants import ORDER_RECEIVED, ORDER_STATUSES, PAYMENT_CASH, PAYMENT_PAID
from src.services.errors import ValidationError

MAX_PAGE_SIZE = 100

def page_offset(page, page_size):
    if not isinstance(page, int) or page < 1:
        raise ValidationError("Номер сторінки має бути цілим числом від 1")
    if not isinstance(page_size, int) or not 1 <= page_size <= MAX_PAGE_SIZE:
        raise ValidationError(f"Розмір сторінки має бути від 1 до {MAX_PAGE_SIZE}")
    return (page - 1) * page_size

def search_authors(session, name, page=1, page_size=10):
    if not name or not name.strip():
        raise ValidationError("Введіть ім'я або прізвище для пошуку")
    offset = page_offset(page, page_size)
    pattern = f"%{name.strip()}%"
    query = (
        select(Author)
        .where(or_(Author.first_name.ilike(pattern), Author.last_name.ilike(pattern)))
        .order_by(Author.last_name, Author.first_name, Author.id)
        .limit(page_size)
        .offset(offset)
    )
    return session.scalars(query).all()

def customer_orders(session, customer_id, status=None, page=1, page_size=10):
    if status is not None and status not in ORDER_STATUSES:
        raise ValidationError(f"Невідомий статус замовлення \"{status}\"")
    offset = page_offset(page, page_size)
    query = (
        select(Orders.id, Orders.date, Orders.status, Address.city, Address.street)
        .join(Address, Address.id == Orders.address_id)
        .where(Orders.customer_id == customer_id)
    )
    if status is not None:
        query = query.where(Orders.status == status)
    query = query.order_by(Orders.date.desc(), Orders.id.desc()).limit(page_size).offset(offset)
    return session.execute(query).all()

def orders_audit(session):
    order_totals = (
        select(
            OrderItem.order_id,
            func.count().label("items_count"),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label("items_total"),
        )
        .group_by(OrderItem.order_id)
        .cte("order_totals")
    )
    items_total = func.coalesce(order_totals.c.items_total, 0)

    audit = (
        select(
            Orders.id.label("order_id"),
            Orders.status,
            func.coalesce(order_totals.c.items_count, 0).label("items_count"),
            items_total.label("items_total"),
            Payment.amount.label("paid_amount"),
            Payment.method,
            Payment.status.label("payment_status"),
            case((order_totals.c.order_id.is_(None), True), else_=False).label("empty_order"),
            case((Payment.id.is_(None), True), else_=False).label("no_payment"),
            case((Payment.amount != items_total, True), else_=False).label("amount_mismatch"),
            case(
                (and_(Payment.method == PAYMENT_CASH, Payment.status == PAYMENT_PAID,
                      Orders.status != ORDER_RECEIVED), True),
                else_=False,
            ).label("cash_paid_early"),
        )
        .outerjoin(order_totals, order_totals.c.order_id == Orders.id)
        .outerjoin(Payment, Payment.order_id == Orders.id)
        .cte("audit")
    )

    query = (
        select(audit)
        .where(or_(audit.c.empty_order, audit.c.no_payment, audit.c.amount_mismatch, audit.c.cash_paid_early))
        .order_by(audit.c.order_id)
    )
    return session.execute(query).all()
