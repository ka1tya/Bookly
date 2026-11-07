from __future__ import annotations

from decimal import Decimal

from sqlalchemy import CheckConstraint, Column, ForeignKey, Identity, Numeric, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

book_category = Table(
    "book_category",
    Base.metadata,
    Column("book_id", ForeignKey("book.id"), primary_key=True),
    Column("category_id", ForeignKey("category.id"), primary_key=True),
)

class Author(Base):
    __tablename__ = "author"

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))

    books: Mapped[list[Book]] = relationship(back_populates="author")

class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    category_name: Mapped[str] = mapped_column(String(60), unique=True)

    books: Mapped[list[Book]] = relationship(secondary=book_category, back_populates="categories")

class Book(Base):
    __tablename__ = "book"
    __table_args__ = (
        CheckConstraint("published_year > 0"),
        CheckConstraint("price >= 0"),
    )

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("author.id"))
    title: Mapped[str] = mapped_column(String(200))
    published_year: Mapped[int | None]
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    author: Mapped[Author] = relationship(back_populates="books")
    categories: Mapped[list[Category]] = relationship(secondary=book_category, back_populates="books")
