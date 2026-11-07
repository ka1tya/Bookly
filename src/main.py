from sqlalchemy import func, select

from src.db import get_session
from src.models import Base

def main():
    with get_session() as session:
        print("Підключення до бази: OK\n")
        for table in Base.metadata.sorted_tables:
            count = session.scalar(select(func.count()).select_from(table))
            print(f"{table.name:<15}{count:>7}")

if __name__ == "__main__":
    main()
