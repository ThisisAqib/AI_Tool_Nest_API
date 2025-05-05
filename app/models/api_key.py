from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from .base import TimestampModel


class KeyStatus(str, Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class APIKey(TimestampModel, table=True):
    __tablename__ = "api_keys"

    id: Optional[int] = Field(default=None, primary_key=True)
    key_prefix: str = Field(index=True)  # First few chars of the key for reference
    key_hash: str  # Hashed API key
    name: str  # User-provided name for the key
    status: KeyStatus = Field(default=KeyStatus.ACTIVE)
    expires_at: Optional[datetime] = Field(default=None)
    last_used_at: Optional[datetime] = Field(default=None)
    revoked_at: Optional[datetime] = Field(default=None)

    # Relationships
    user_id: int = Field(foreign_key="users.id")
    user: "User" = Relationship(back_populates="api_keys")
    usage_logs: List["APIKeyUsage"] = Relationship(back_populates="api_key")
