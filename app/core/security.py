import secrets
import hashlib
from typing import Tuple, Any, Union
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(
    data: dict[str, Any], expires_delta: Union[timedelta, None] = None
) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str) -> Union[dict[str, Any], None]:
    """Verify JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        return None


def generate_api_key() -> str:
    """Generate a new API key."""
    return secrets.token_urlsafe(32)


def get_api_key_hash(api_key: str) -> str:
    """
    Generate a hash for an API key.

    Args:
        api_key: The API key to hash

    Returns:
        str: The hashed API key
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(api_key: str, stored_hash: str) -> bool:
    """
    Verify an API key against its stored hash.

    Args:
        api_key: The API key to verify
        stored_hash: The stored hash to verify against

    Returns:
        bool: True if the API key is valid
    """
    return get_api_key_hash(api_key) == stored_hash
