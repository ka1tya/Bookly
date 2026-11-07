import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://bookly:bookly_password@localhost:5432/bookly")
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql+psycopg://bookly:bookly_password@localhost:5433/bookly_test")

engine = create_engine(DATABASE_URL)
get_session = sessionmaker(bind=engine, expire_on_commit=False)
