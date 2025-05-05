from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class APIKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class APIKeyResponse(BaseModel):
    id: int
    name: str
    key_prefix: str
    status: str
    created_at: datetime
    last_used_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None


class APIKeyCreateResponse(APIKeyResponse):
    api_key: str  # Full API key, only shown once at creation


class APIKeyList(BaseModel):
    api_keys: list[APIKeyResponse]


class APIKeyUsageEntry(BaseModel):
    """Schema for individual API key usage entry"""

    endpoint: str
    method: str
    status_code: int
    response_time: float
    ip_address: str
    user_agent: Optional[str] = None
    created_at: datetime


class APIKeyUsageStats(BaseModel):
    """Schema for API key usage statistics"""

    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    usage_by_endpoint: dict[str, int]
    recent_usage: List[APIKeyUsageEntry]
