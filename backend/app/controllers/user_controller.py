"""
User controller for authentication API endpoints
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.controllers.base_controller import BaseController
from app.services.user_service import UserService
from app.schemas.user_schemas import (
    UserCreate, UserResponse, LoginRequest, LoginResponse
)

security = HTTPBearer()


class UserController(BaseController):
    """Controller for user authentication API endpoints"""
    
    def __init__(self):
        super().__init__()
        self.user_service = UserService()
    
    def register(self, user_data: UserCreate) -> UserResponse:
        """Register a new user"""
        try:
            return self.user_service.create_user(user_data)
        except Exception as e:
            self.handle_error(e, "Error creating user")
    
    def login(self, login_data: LoginRequest) -> LoginResponse:
        """Login user and return access token"""
        try:
            return self.user_service.authenticate_user(login_data)
        except Exception as e:
            self.handle_error(e, "Error during login")
    
    def get_current_user(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> UserResponse:
        """Get current authenticated user"""
        try:
            token = credentials.credentials
            return self.user_service.get_current_user(token)
        except Exception as e:
            self.handle_error(e, "Error getting current user")
    
    def get_profile(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> UserResponse:
        """Get user profile"""
        try:
            token = credentials.credentials
            return self.user_service.get_current_user(token)
        except Exception as e:
            self.handle_error(e, "Error getting user profile")


# Helper function for dependency injection
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserResponse:
    """Dependency to get current user"""
    controller = UserController()
    return controller.get_current_user(credentials)
