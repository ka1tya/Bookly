from sqlalchemy import exists, insert, select

from src.models import Book, OrderItem, book_category


def lock_book(session, book_id, nowait=False):
    return session.get(Book, book_id, with_for_update={"nowait": nowait}, populate_existing=True)


def add_categories(session, book_id, category_ids):
    rows = [{"book_id": book_id, "category_id": c} for c in category_ids]
    session.execute(insert(book_category), rows)


def in_orders(session, book_id):
    return session.scalar(select(exists().where(OrderItem.book_id == book_id)))
