"""API request/response şemaları (auth + polls)."""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PollCreate(BaseModel):
    question: str = Field(min_length=1, max_length=280)
    options: list[str] = Field(min_length=2, max_length=5)

    @field_validator("question")
    @classmethod
    def strip_question(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Soru metni boş olamaz")
        return v

    @field_validator("options")
    @classmethod
    def validate_options(cls, options: list[str]) -> list[str]:
        cleaned = [o.strip() for o in options]
        if any(not o for o in cleaned):
            raise ValueError("Seçenek metni boş olamaz")
        if any(len(o) > 120 for o in cleaned):
            raise ValueError("Bir seçenek en fazla 120 karakter olabilir")
        return cleaned


class VoteRequest(BaseModel):
    option_id: int


class PollOptionRead(BaseModel):
    id: int
    text: str
    votes: int
    percentage: float


class PollListItem(BaseModel):
    id: int
    question: str
    created_by: str
    total_votes: int
    created_at: datetime


class PollDetail(PollListItem):
    options: list[PollOptionRead]
    voted_option_id: int | None = None
