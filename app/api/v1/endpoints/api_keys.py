from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.services.api_key_service import APIKeyService
from app.schemas.api_key import (
    APIKeyCreate,
    APIKeyCreateResponse,
    APIKeyResponse,
    APIKeyList,
    APIKeyUsageStats,
)
from app.api.deps import get_current_user
from app.models import User
from app.core.rate_limit import limiter

router = APIRouter()


@router.post("/", response_model=APIKeyCreateResponse)
@limiter.limit("2/minute")
async def create_api_key(
    request: Request,
    key_create: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Create a new API key for the current user."""
    api_key_service = APIKeyService(session)
    db_key, api_key = await api_key_service.create_api_key(
        user_id=current_user.id, name=key_create.name
    )

    return APIKeyCreateResponse(
        id=db_key.id,
        name=db_key.name,
        key_prefix=db_key.key_prefix,
        status=db_key.status,
        created_at=db_key.created_at,
        last_used_at=db_key.last_used_at,
        revoked_at=db_key.revoked_at,
        api_key=api_key,  # Only returned once at creation
    )


@router.get("/", response_model=APIKeyList)
@limiter.limit("10/minute")
async def list_api_keys(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """List all API keys for the current user."""
    api_key_service = APIKeyService(session)
    keys = await api_key_service.get_user_api_keys(current_user.id)

    return APIKeyList(
        api_keys=[
            APIKeyResponse(
                id=key.id,
                name=key.name,
                key_prefix=key.key_prefix,
                status=key.status,
                created_at=key.created_at,
                last_used_at=key.last_used_at,
                revoked_at=key.revoked_at,
            )
            for key in keys
        ]
    )


@router.get("/{key_id}/usage", response_model=APIKeyUsageStats)
@limiter.limit("10/minute")
async def get_api_key_usage(
    request: Request,
    key_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get usage statistics for an API key.

    Args:
        key_id: The ID of the API key to get usage for
        current_user: The authenticated user
        session: Database session

    Returns:
        APIKeyUsageStats: Usage statistics for the API key

    Raises:
        HTTPException: If the API key doesn't exist or doesn't belong to the user
    """
    api_key_service = APIKeyService(session)
    stats = await api_key_service.get_key_usage_stats(key_id, current_user.id)

    if not stats:
        raise HTTPException(status_code=404, detail="API key not found")

    return stats


@router.delete("/{key_id}", response_model=APIKeyResponse)
@limiter.limit("2/minute")
async def revoke_api_key(
    request: Request,
    key_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Revoke an API key."""
    api_key_service = APIKeyService(session)
    key = await api_key_service.revoke_api_key(key_id, current_user.id)

    if not key:
        raise HTTPException(
            status_code=404, detail="API key not found or already revoked"
        )

    return APIKeyResponse(
        id=key.id,
        name=key.name,
        key_prefix=key.key_prefix,
        status=key.status,
        created_at=key.created_at,
        last_used_at=key.last_used_at,
        revoked_at=key.revoked_at,
    )
