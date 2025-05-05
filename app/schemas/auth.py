from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """Schema for authentication token response"""

    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    """Schema for login request"""

    username: str  # Can be username or email
    password: str


class UserBase(BaseModel):
    """Base schema for user data"""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    """Schema for user creation request"""

    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    """Schema for user response"""

    id: int
    is_active: bool

    class Config:
        from_attributes = True
