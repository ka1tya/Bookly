import pytest

from src.models import Book, Orders
from src.models.constants import ORDER_CANCELLED
from src.repositories.book_queries import book_revenue_ranking, books_in_category, search_by_title
from src.services.errors import ValidationError

pytestmark = pytest.mark.integration

THRILLER = 6


def titles(books):
    return [book.title for book in books]


def ranking_of(session, category):
    return [(row.title, row.revenue, row.place) for row in book_revenue_ranking(session)
            if row.category_name == category]


def test_search_by_title(session):
    assert titles(search_by_title(session, "во")) == ["Вбивство у Східному експресі", "Воно"]


def test_search_any_case(session):
    assert titles(search_by_title(session, "КОБЗАР")) == ["Кобзар"]


def test_search_with_spaces(session):
    assert titles(search_by_title(session, "  воно  ")) == ["Воно"]


def test_search_second_page(session):
    assert titles(search_by_title(session, "во", page=2, page_size=1)) == ["Воно"]


def test_search_nothing_found(session):
    assert search_by_title(session, "Такої книги немає") == []


def test_search_percent_is_not_wildcard(session):
    assert search_by_title(session, "%") == []


def test_search_wrong_page(session):
    with pytest.raises(ValidationError):
        search_by_title(session, "во", page=0)


def test_books_in_category(session):
    books = books_in_category(session, THRILLER)
    assert titles(books) == ["Переслідування Аделіни", "Воно", "Бійцівський клуб"]
    assert [float(book.price) for book in books] == [430, 420, 300]


def test_books_in_category_max_price(session):
    assert titles(books_in_category(session, THRILLER, max_price=420)) == ["Воно", "Бійцівський клуб"]


def test_books_in_category_second_page(session):
    assert titles(books_in_category(session, THRILLER, page=2, page_size=2)) == ["Бійцівський клуб"]


def test_empty_category(session):
    assert books_in_category(session, 5) == []


def test_missing_category(session):
    assert books_in_category(session, 999) == []


def test_revenue_ranking(session):
    rows = book_revenue_ranking(session)
    assert [(row.category_name, row.title, row.sold, row.revenue, row.place) for row in rows] == [
        ("Детектив", "Вбивство у Східному експресі", 1, 260, 1),
        ("Жахи", "Воно", 0, 0, 1),
        ("Поезія", "Маруся Чурай", 1, 200, 1),
        ("Поезія", "Кобзар", 0, 0, 2),
        ("Романтика", "Переслідування Аделіни", 0, 0, 1),
        ("Трилер", "Бійцівський клуб", 2, 600, 1),
        ("Трилер", "Воно", 0, 0, 2),
        ("Трилер", "Переслідування Аделіни", 0, 0, 2),
        ("Фентезі", "Гаррі Поттер і філософський камінь", 1, 350, 1),
    ]


def test_ranking_without_cancelled(session):
    assert ("Переслідування Аделіни", 0, 2) in ranking_of(session, "Трилер")


def test_ranking_after_new_sale(session, make_order_item):
    make_order_item(book=session.get(Book, 3), quantity=2)

    assert ranking_of(session, "Трилер") == [
        ("Воно", 840, 1),
        ("Бійцівський клуб", 600, 2),
        ("Переслідування Аделіни", 0, 3),
    ]


def test_ranking_after_cancel(session):
    session.get(Orders, 2).status = ORDER_CANCELLED
    session.flush()

    assert [place for _, _, place in ranking_of(session, "Трилер")] == [1, 1, 1]
