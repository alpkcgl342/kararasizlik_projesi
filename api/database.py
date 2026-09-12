"""SQLAlchemy engine / session kurulumu.

Serverless (Vercel) ortamında her istek yeni bir bağlantı açabileceğinden,
Supabase'in pgbouncer (transaction mode) connection pooling'i kullanılmalı ve
burada NullPool tercih edilmelidir (bağlantı, istek bitince serbest bırakılır,
uygulama içinde ayrıca bir pool tutulmaz).
"""
from collections.abc import Generator

from sqlalchemy.pool import NullPool
from sqlmodel import Session, create_engine

from api.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    poolclass=NullPool,
    echo=False,
)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
