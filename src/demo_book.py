from src.db import get_session
from src.repositories.book_queries import book_revenue_ranking, books_in_category, search_by_title


def main():
    with get_session() as session:
        print("Пошук книг за назвою «во»:")
        for book in search_by_title(session, "во"):
            print(f"  {book.title}, {book.price} грн")

        print("\nКниги категорії «Трилер» до 450 грн:")
        for book in books_in_category(session, 6, max_price=450):
            print(f"  {book.title}, {book.price} грн")

        print("\nНайприбутковіші книги в кожній категорії:")
        for row in book_revenue_ranking(session):
            print(f"  {row.category_name}: {row.place}. {row.title}, продано {row.sold}, виручка {row.revenue}")


if __name__ == "__main__":
    main()
