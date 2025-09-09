"""
User authentication schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.user_models import UserRole


class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """User creation model"""
    password: str


class UserUpdate(BaseModel):
    """User update model"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """User response model"""
    id: int
    role: UserRole
    created_at: datetime
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Login request model"""
    username: str  # Changed from email to username to match frontend
    password: str


class LoginResponse(BaseModel):
    """Login response model"""
    access_token: str
    token_type: str = "bearer"
    user: Optional[UserResponse] = None
    user: UserResponse


class TokenData(BaseModel):
    """Token data model"""
    email: Optional[str] = None
