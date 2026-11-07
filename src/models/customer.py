from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Identity, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.order import Orders

class Customer(Base):
    __tablename__ = "customer"

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True)

    addresses: Mapped[list[Address]] = relationship(
        back_populates="customer", cascade="all, delete-orphan", passive_deletes=True
    )
    orders: Mapped[list[Orders]] = relationship(back_populates="customer", passive_deletes="all")

class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id", ondelete="CASCADE"))
    country: Mapped[str] = mapped_column(String(100))
    city: Mapped[str] = mapped_column(String(100))
    street: Mapped[str] = mapped_column(String(255))
    postal_code: Mapped[str | None] = mapped_column(String(20))

    customer: Mapped[Customer] = relationship(back_populates="addresses")
    orders: Mapped[list[Orders]] = relationship(back_populates="address", passive_deletes="all")
