"""SQLModel tabloları (bkz. docs/kararsizim-proje-plani.md, Bölüm 7).

Not: (poll_id, user_id) ve (poll_id, guest_id) için "sadece ilgili sütun NULL
değilken" geçerli olan partial unique index'ler Alembic migration'ında elle
tanımlanır (SQLModel/SQLAlchemy Core seviyesinde ifade edilemedikleri için) —
bkz. alembic/versions/xxxx_initial_schema.py.
"""
from datetime import datetime, timezone
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, max_length=32)
    email: str = Field(unique=True, index=True)
    password_hash: str
    created_at: datetime = Field(default_factory=utcnow)

    polls: list["Poll"] = Relationship(back_populates="created_by")


class Poll(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    question: str = Field(max_length=280)
    created_by_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=utcnow)

    created_by: User | None = Relationship(back_populates="polls")
    options: list["PollOption"] = Relationship(back_populates="poll")


class PollOption(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    poll_id: int = Field(foreign_key="poll.id")
    text: str = Field(max_length=120)
    order: int = Field(default=0)

    poll: Poll | None = Relationship(back_populates="options")


class Vote(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    poll_id: int = Field(foreign_key="poll.id")
    option_id: int = Field(foreign_key="polloption.id")
    user_id: int | None = Field(default=None, foreign_key="user.id")
    guest_id: UUID | None = Field(default=None)
    created_at: datetime = Field(default_factory=utcnow)
