"""
Authentication utilities and dependencies
"""
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config.settings import config
from app.repositories.user_repository import UserRepository
from app.models.user_models import User, UserRole

# JWT token handling
security = HTTPBearer()


class AuthUtils:
    """Authentication utility functions"""
    
    SECRET_KEY = "your-secret-key-change-in-production"  # Change this in production!
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=AuthUtils.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, AuthUtils.SECRET_KEY, algorithm=AuthUtils.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, AuthUtils.SECRET_KEY, algorithms=[AuthUtils.ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None


# FastAPI Dependencies
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = AuthUtils.verify_token(token)
    
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")  # Changed from user_id to username
    if username is None:
        raise credentials_exception
    
    user_repo = UserRepository()
    user = user_repo.find_by_username(username)  # Find by username instead
    
    if user is None:
        raise credentials_exception
    
    # Convert dict to User model
    return User(
        id=user['id'],
        email=user['email'],
        username=user['username'],
        full_name=user['full_name'],
        password_hash=user['password_hash'],
        role=UserRole(user['role']),
        is_active=bool(user['is_active']),
        created_at=datetime.fromisoformat(user['created_at'])
    )


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Require admin user"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# Optional authentication (allows None if no token provided)
async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[User]:
    """Get current user if token provided, otherwise None"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = AuthUtils.verify_token(token)
        
        if payload is None:
            return None
        
        username: str = payload.get("sub")  # Changed from user_id to username
        if username is None:
            return None
        
        user_repo = UserRepository()
        user_data = user_repo.find_by_username(username)  # Find by username
        
        if not user_data:
            return None
        
        # Convert dict to User model
        user = User(
            id=user_data['id'],
            email=user_data['email'],
            username=user_data['username'],
            full_name=user_data['full_name'],
            password_hash=user_data['password_hash'],
            role=UserRole(user_data['role']),
            is_active=bool(user_data['is_active']),
            created_at=datetime.fromisoformat(user_data['created_at'])
        )
        
        return user if user.is_active else None
    except:
        return None