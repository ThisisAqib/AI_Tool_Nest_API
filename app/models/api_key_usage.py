from typing import Optional
from sqlmodel import Field, Relationship
from .base import TimestampModel


class APIKeyUsage(TimestampModel, table=True):
    __tablename__ = "api_key_usage"

    id: Optional[int] = Field(default=None, primary_key=True)
    endpoint: str = Field(index=True)  # The endpoint that was accessed
    method: str  # HTTP method used
    status_code: int  # Response status code
    response_time: float  # Response time in seconds
    ip_address: str  # Client IP address
    user_agent: Optional[str] = None  # Client user agent

    # Relationships
    api_key_id: int = Field(foreign_key="api_keys.id")
    api_key: "APIKey" = Relationship(back_populates="usage_logs")
