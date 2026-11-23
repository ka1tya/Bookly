from sqlalchemy import func, select

from src.models import Book, Category, OrderItem, Orders, book_category
from src.models.constants import ORDER_CANCELLED
from src.services.errors import ValidationError


def page_offset(page, page_size):
    if page < 1 or page_size < 1:
        raise ValidationError("Номер сторінки і її розмір мають бути більшими за 0")
    return (page - 1) * page_size


def search_by_title(session, text, page=1, page_size=10):
    offset = page_offset(page, page_size)
    text = text.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    query = (
        select(Book)
        .where(Book.title.ilike(f"%{text}%", escape="\\"))
        .order_by(Book.title, Book.id)
        .limit(page_size)
        .offset(offset)
    )
    return session.scalars(query).all()


def books_in_category(session, category_id, max_price=None, page=1, page_size=10):
    offset = page_offset(page, page_size)
    query = (
        select(Book)
        .join(book_category, book_category.c.book_id == Book.id)
        .where(book_category.c.category_id == category_id)
    )
    if max_price is not None:
        query = query.where(Book.price <= max_price)
    query = query.order_by(Book.price.desc(), Book.title, Book.id).limit(page_size).offset(offset)
    return session.scalars(query).all()


def book_revenue_ranking(session):
    sales = (
        select(
            OrderItem.book_id,
            func.sum(OrderItem.quantity).label("sold"),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label("revenue"),
        )
        .join(Orders, Orders.id == OrderItem.order_id)
        .where(Orders.status != ORDER_CANCELLED)
        .group_by(OrderItem.book_id)
        .cte("book_sales")
    )
    revenue = func.coalesce(sales.c.revenue, 0)
    query = (
        select(
            Category.category_name,
            Book.title,
            func.coalesce(sales.c.sold, 0).label("sold"),
            revenue.label("revenue"),
            func.rank().over(partition_by=Category.id, order_by=revenue.desc()).label("place"),
        )
        .join(book_category, book_category.c.category_id == Category.id)
        .join(Book, Book.id == book_category.c.book_id)
        .outerjoin(sales, sales.c.book_id == Book.id)
        .order_by(Category.category_name, "place", Book.title)
    )
    return session.execute(query).all()
