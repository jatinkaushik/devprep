"""
User repository for database operations
"""
from typing import List, Optional
from app.repositories.base_repository import BaseRepository
from app.schemas.user_schemas import UserCreate


class UserRepository(BaseRepository):
    """Repository for user-related database operations"""
    
    def find_all(self, **kwargs) -> List[dict]:
        """Find all users"""
        query = "SELECT id, email, username, full_name, is_active, created_at FROM users"
        return self.execute_query(query)
    
    def find_by_id(self, id: int) -> Optional[dict]:
        """Find user by ID"""
        query = "SELECT id, email, username, full_name, is_active, created_at FROM users WHERE id = ?"
        return self.execute_query_one(query, (id,))
    
    def find_by_email(self, email: str) -> Optional[dict]:
        """Find user by email"""
        query = "SELECT * FROM users WHERE email = ?"
        return self.execute_query_one(query, (email,))
    
    def find_by_username(self, username: str) -> Optional[dict]:
        """Find user by username"""
        query = "SELECT * FROM users WHERE username = ?"
        return self.execute_query_one(query, (username,))
    
    def create_user(self, user_data: UserCreate, hashed_password: str) -> dict:
        """Create a new user"""
        query = """
            INSERT INTO users (email, username, full_name, password_hash, is_active)
            VALUES (?, ?, ?, ?, ?)
        """
        
        with self.db_manager.get_connection() as conn:
            cursor = self.db_manager.get_cursor(conn)
            cursor.execute(query, (
                user_data.email,
                user_data.username,
                user_data.full_name,
                hashed_password,
                user_data.is_active
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
        
        with self.db_manager.get_connection() as conn:
            cursor = self.db_manager.get_cursor(conn)
            cursor.execute(query, params)
            conn.commit()
        
        return self.find_by_id(user_id)
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user (soft delete by setting is_active to False)"""
        return self.update_user(user_id, is_active=False) is not None
