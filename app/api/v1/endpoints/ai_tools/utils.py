"""
AI Tools Utilities

Shared functionality for AI tool endpoints.
"""

from time import time
from typing import Optional, Tuple
from fastapi import HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.core.database import get_session
from app.services.api_key_service import APIKeyService

# API key header scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


async def get_current_user_by_api_key(
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_session),
) -> Tuple[User, int]:
    """
    Get the current user from API key authentication.

    Args:
        api_key: API key from X-API-Key header
        session: Database session

    Returns:
        Tuple[User, int]: The authenticated user and API key ID

    Raises:
        HTTPException: If API key is invalid or missing
    """
    api_key_service = APIKeyService(session)
    key = await api_key_service.verify_and_update_key(api_key)

    if not key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "APIKey"},
        )

    # Get user
    user_query = select(User).where(User.id == key.user_id)
    result = await session.execute(user_query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "APIKey"},
        )

    return user, key.id


async def log_api_usage(
    api_key_id: int,
    endpoint: str,
    method: str,
    status_code: int,
    response_time: float,
    ip_address: Optional[str],
    user_agent: Optional[str],
    session: AsyncSession,
) -> None:
    """
    Log API key usage for analytics and rate limiting.

    Args:
        api_key_id: The ID of the API key used
        endpoint: The endpoint path
        method: The HTTP method (GET, POST, etc.)
        status_code: HTTP status code of the response
        response_time: Time taken to process the request
        ip_address: Client IP address
        user_agent: Client user agent
        session: Database session
    """
    api_key_service = APIKeyService(session)
    await api_key_service.log_api_key_usage(
        api_key_id=api_key_id,
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        response_time=response_time,
        ip_address=ip_address,
        user_agent=user_agent,
    )
