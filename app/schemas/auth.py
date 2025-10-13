"""Pydantic schemas for authentication and user management."""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user creation."""
    password: str


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    is_active: bool
    is_verified: bool
    tier: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for authentication tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token data."""
    user_id: Optional[int] = None


class PasswordReset(BaseModel):
    """Schema for password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str
    new_password: str


class EmailVerification(BaseModel):
    """Schema for email verification."""
    token: str


class ChangePassword(BaseModel):
    """Schema for password change."""
    current_password: str
    new_password: str


class FirebaseTokenRequest(BaseModel):
    """Schema for Firebase token verification request."""
    idToken: str


class FirebaseUserResponse(BaseModel):
    """Schema for Firebase user response."""
    uid: str
    email: str
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    email_verified: bool = False


# Request bodies
class RefreshRequest(BaseModel):
    """Schema for refresh token request body."""
    refresh_token: str
