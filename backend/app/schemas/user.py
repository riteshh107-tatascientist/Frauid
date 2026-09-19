"""
User-related Pydantic schemas.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """User registration request schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    """User login request schema"""
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Password")


class UserResponse(BaseModel):
    """User response schema (never includes password_hash)"""
    id: int
    username: str
    email: str
    role: str = Field(default="USER", description="USER or ADMIN")
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "username": "demouser",
                "email": "demo@example.com",
                "role": "USER",
                "is_active": True,
                "created_at": "2026-09-17T10:00:00"
            }
        }


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenPayload(BaseModel):
    """JWT token payload schema"""
    sub: int  # user_id
    exp: Optional[datetime] = None
