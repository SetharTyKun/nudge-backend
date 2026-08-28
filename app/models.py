from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=utc_now)

    notes: list["Note"] = Relationship(back_populates="owner")


class Note(SQLModel, table=True):
    __tablename__ = "notes"

    id: int | None = Field(default=None, primary_key=True)
    title: str
    content: str
    is_pinned: bool = Field(default=False)
    is_completed: bool = Field(default=False)

    owner_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    owner: User | None = Relationship(back_populates="notes")
