from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.core.database import get_session
from app.models.user import User
from app.schemas.auth import Token, UserCreate, UserResponse, LoginRequest
from app.core.rate_limit import limiter


router = APIRouter()


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(
    request: Request,
    login_data: LoginRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Login endpoint to get an access token.

    Args:
        login_data: Username/email and password
        session: Database session

    Returns:
        Token: Access token for authentication

    Raises:
        HTTPException: If credentials are invalid or user is inactive
    """
    # Find user by username/email
    query = select(User).where(
        (User.username == login_data.username) | (User.email == login_data.username)
    )
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user"
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")


@router.post("/register", response_model=UserResponse)
@limiter.limit("5/minute")
async def register(
    request: Request, user_in: UserCreate, session: AsyncSession = Depends(get_session)
):
    """
    Register a new user.

    Args:
        user_in: User registration data
        session: Database session

    Returns:
        UserResponse: Created user information

    Raises:
        HTTPException: If username or email already exists
    """
    # Check if username or email already exists
    query = select(User).where(
        (User.username == user_in.username) | (User.email == user_in.email)
    )
    result = await session.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    # Create new user
    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return UserResponse.model_validate(user)
