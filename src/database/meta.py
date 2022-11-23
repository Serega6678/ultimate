import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

DB_URL = os.getenv("DB_URL")
assert DB_URL is not None

engine = create_engine(DB_URL)

Base = declarative_base()
