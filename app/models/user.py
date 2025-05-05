from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from .base import TimestampModel


class User(TimestampModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)

    # Relationships
    api_keys: List["APIKey"] = Relationship(back_populates="user")

    class Config:
        arbitrary_types_allowed = True
