from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.auth import verify_token
from app.core.database import get_session
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/endpoints/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)
) -> User:
    """
    Get the current authenticated user based on the JWT token.

    Args:
        token: JWT token from the Authorization header
        session: Database session

    Returns:
        User: The authenticated user

    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify the token
    payload = verify_token(token)
    if not payload:
        raise credentials_exception

    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        # Ensure user_id is an integer
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise credentials_exception

    # Get the user from database
    query = select(User).where(User.id == user_id, User.is_active == True)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get the current authenticated superuser.

    Args:
        current_user: The current authenticated user

    Returns:
        User: The authenticated superuser

    Raises:
        HTTPException: If the user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user
