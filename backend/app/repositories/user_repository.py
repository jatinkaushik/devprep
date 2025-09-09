"""
User repository for database operations
"""
from typing import List, Optional
from datetime import datetime
from app.config.database import get_db_connection
from app.models.user_models import User, UserRole
from app.schemas.user_schemas import UserCreate


class UserRepository:
    """Repository for user-related database operations"""
    
    def find_all(self, **kwargs) -> List[dict]:
        """Find all users"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT id, email, username, full_name, role, is_active, created_at FROM users"
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]
    
    def find_by_id(self, id: int) -> Optional[dict]:
        """Find user by ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT id, email, username, full_name, role, is_active, created_at FROM users WHERE id = ?"
            cursor.execute(query, (id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_user_by_id(self, id: int) -> Optional[User]:
        """Get User model by ID"""
        user_data = self.find_by_id(id)
        if not user_data:
            return None
        
        return User(
            id=user_data['id'],
            email=user_data['email'],
            username=user_data['username'],
            full_name=user_data['full_name'],
            password_hash='',  # Don't expose password hash
            role=UserRole(user_data['role']),
            is_active=bool(user_data['is_active']),
            created_at=datetime.fromisoformat(user_data['created_at'])
        )
    
    def find_by_email(self, email: str) -> Optional[dict]:
        """Find user by email"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM users WHERE email = ?"
            cursor.execute(query, (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def find_by_username(self, username: str) -> Optional[dict]:
        """Find user by username"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM users WHERE username = ?"
            cursor.execute(query, (username,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def create_user(self, user_data: UserCreate, hashed_password: str, role: UserRole = UserRole.USER) -> dict:
        """Create a new user"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = """
                INSERT INTO users (email, username, full_name, password_hash, role, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (
                user_data.email,
                user_data.username,
                user_data.full_name,
                hashed_password,
                role.value,
                True  # Default to active
            ))
            conn.commit()
            user_id = cursor.lastrowid
        
        # Return the created user
        return self.find_by_id(user_id)
    
    def update_user(self, user_id: int, **kwargs) -> Optional[dict]:
        """Update user data"""
        if not kwargs:
            return self.find_by_id(user_id)
        
        # Build dynamic update query
        set_clauses = []
        params = []
        
        for key, value in kwargs.items():
            if value is not None:
                set_clauses.append(f"{key} = ?")
                params.append(value)
        
        if not set_clauses:
            return self.find_by_id(user_id)
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = ?"
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
        
        return self.find_by_id(user_id)
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user (soft delete by setting is_active to False)"""
        return self.update_user(user_id, is_active=False) is not None
