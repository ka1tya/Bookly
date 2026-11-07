from __future__ import annotations

import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Identity, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.catalog import Book
    from src.models.customer import Address, Customer

class Orders(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id", ondelete="RESTRICT"))
    address_id: Mapped[int] = mapped_column(ForeignKey("address.id", ondelete="RESTRICT"))
    date: Mapped[datetime.date] = mapped_column(Date, server_default=func.current_date())
    status: Mapped[str] = mapped_column(String(20), server_default="нове")

    customer: Mapped[Customer] = relationship(back_populates="orders")
    address: Mapped[Address] = relationship(back_populates="orders")
    items: Mapped[list[OrderItem]] = relationship(back_populates="order")
    payment: Mapped[Payment | None] = relationship(back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_item"

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("book.id"), primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    order: Mapped[Orders] = relationship(back_populates="items")
    book: Mapped[Book] = relationship()

class Payment(Base):
    __tablename__ = "payment"

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), unique=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    date: Mapped[datetime.date] = mapped_column(Date, server_default=func.current_date())
    method: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), server_default="очікує")

    order: Mapped[Orders] = relationship(back_populates="payment")
