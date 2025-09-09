"""
User service for business logic
"""
from typing import Optional
from fastapi import HTTPException
from app.services.base_service import BaseService
from app.repositories.user_repository import UserRepository
from app.schemas.user_schemas import (
    UserCreate, UserResponse, LoginRequest, LoginResponse
)
from app.utils.auth import AuthUtils


class UserService(BaseService):
    """Service for user-related business logic"""
    
    def __init__(self):
        super().__init__()
        self.user_repo = UserRepository()
        self.auth_utils = AuthUtils()
    
    def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user"""
        # Check if user already exists
        existing_user = self.user_repo.find_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists"
            )
        
        existing_username = self.user_repo.find_by_username(user_data.username)
        if existing_username:
            raise HTTPException(
                status_code=400,
                detail="Username already taken"
            )
        
        # Hash password
        hashed_password = self.auth_utils.hash_password(user_data.password)
        
        # Create user
        user = self.user_repo.create_user(user_data, hashed_password)
        return UserResponse(**user)
    
    def authenticate_user(self, login_data: LoginRequest) -> LoginResponse:
        """Authenticate user and return access token"""
        # Find user by username (changed from email)
        user = self.user_repo.find_by_username(login_data.username)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )
        
        # Check if user is active
        if not user['is_active']:
            raise HTTPException(
                status_code=401,
                detail="Account is disabled"
            )
        
        # Verify password
        if not self.auth_utils.verify_password(login_data.password, user['password_hash']):
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )
        
        # Create access token
        access_token = self.auth_utils.create_access_token(
            data={"sub": user['username'], "user_id": user['id']}  # Include user_id in token
        )
        
        # Remove password hash from user data
        user_data = {k: v for k, v in user.items() if k != 'password_hash'}
        
        return LoginResponse(
            access_token=access_token,
            user=UserResponse(**user_data)
        )
    
    def get_current_user(self, token: str) -> UserResponse:
        """Get current user from token"""
        payload = self.auth_utils.verify_token(token)
        if not payload:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )
        
        username = payload.get("sub")  # Changed from email to username
        if not username:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )
        
        user = self.user_repo.find_by_username(username)  # Changed from email to username
        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )
        
        if not user['is_active']:
            raise HTTPException(
                status_code=401,
                detail="Account is disabled"
            )
        
        # Remove password hash from user data
        user_data = {k: v for k, v in user.items() if k != 'password_hash'}
        return UserResponse(**user_data)
    
    def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        """Get user by ID"""
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return None
        
        return UserResponse(**user)
