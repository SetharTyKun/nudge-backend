from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class NoteCreate(BaseModel):
    content: str = Field(..., min_length=1)
    is_pinned: bool = Field(False)
    is_completed: bool = Field(False)


class NoteUpdate(BaseModel):
    content: str | None = Field(None, min_length=1)
    is_pinned: bool | None = Field(None)
    is_completed: bool | None = Field(None)


class NoteResponse(BaseModel):
    id: int
    # title: str
    content: str
    is_pinned: bool
    is_completed: bool
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NoteListResponse(BaseModel):
    notes: list[NoteResponse]
    total: int
    limit: int
    offset: int


# ----- USER
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str = Field(min_length=8)

    @field_validator("username")
    @classmethod
    def username_must_be_alphanumeric(cls, v: str) -> str:
        if not v.replace("_", "").isalnum():
            raise ValueError("Username must be alphanumeric")
        return v.lower()


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int | None = None
