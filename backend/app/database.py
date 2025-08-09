from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

# Load env vars from .env if present
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

DEFAULT_DB_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/llmchecks"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session