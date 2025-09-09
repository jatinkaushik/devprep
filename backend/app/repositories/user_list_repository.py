"""
User list repository for database operations
"""
from typing import List, Dict, Any, Optional
from app.repositories.base_repository import BaseRepository
from app.models.user_models import ListType, QuestionStatus


class UserListRepository(BaseRepository):
    """Repository for user list operations"""
    
    def get_user_lists(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all lists for a user"""
        query = """
            SELECT ul.*, 
                   COUNT(uli.id) as item_count
            FROM user_lists ul
            LEFT JOIN user_list_items uli ON ul.id = uli.list_id
            WHERE ul.user_id = ?
            GROUP BY ul.id
            ORDER BY ul.is_default DESC, ul.created_at ASC
        """
        return self.execute_query(query, (user_id,))
    
    def create_user_list(self, user_id: int, name: str, list_type: str, description: str = None) -> Dict[str, Any]:
        """Create a new user list"""
        query = """
            INSERT INTO user_lists (user_id, name, list_type, description, is_default)
            VALUES (?, ?, ?, ?, FALSE)
        """
        list_id = self.execute_insert(query, (user_id, name, list_type, description))
        return self.get_user_list_by_id(list_id)
    
    def get_user_list_by_id(self, list_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific user list"""
        query = """
            SELECT ul.*, 
                   COUNT(uli.id) as item_count
            FROM user_lists ul
            LEFT JOIN user_list_items uli ON ul.id = uli.list_id
            WHERE ul.id = ?
            GROUP BY ul.id
        """
        return self.execute_query_one(query, (list_id,))
    
    def delete_user_list(self, list_id: int, user_id: int) -> bool:
        """Delete a user list (only custom lists)"""
        query = """
            DELETE FROM user_lists 
            WHERE id = ? AND user_id = ? AND is_default = FALSE
        """
        return self.execute_update(query, (list_id, user_id)) > 0
    
    def add_item_to_list(self, list_id: int, question_id: int = None, user_question_id: int = None, 
                        status: str = "not_attempted", notes: str = None) -> Dict[str, Any]:
        """Add an item to a user list"""
        # Check if item already exists
        existing_query = """
            SELECT id FROM user_list_items 
            WHERE list_id = ? AND 
                  ((question_id = ? AND question_id IS NOT NULL) OR 
                   (user_question_id = ? AND user_question_id IS NOT NULL))
        """
        existing = self.execute_query_one(existing_query, (list_id, question_id, user_question_id))
        
        if existing:
            return {"error": "Item already exists in list"}
        
        query = """
            INSERT INTO user_list_items (list_id, question_id, user_question_id, status, notes)
            VALUES (?, ?, ?, ?, ?)
        """
        item_id = self.execute_insert(query, (list_id, question_id, user_question_id, status, notes))
        return self.get_list_item_by_id(item_id)
    
    def remove_item_from_list(self, list_id: int, question_id: int = None, user_question_id: int = None) -> bool:
        """Remove an item from a user list"""
        query = """
            DELETE FROM user_list_items 
            WHERE list_id = ? AND 
                  ((question_id = ? AND question_id IS NOT NULL) OR 
                   (user_question_id = ? AND user_question_id IS NOT NULL))
        """
        return self.execute_update(query, (list_id, question_id, user_question_id)) > 0
    
    def get_list_items(self, list_id: int) -> List[Dict[str, Any]]:
        """Get all items in a list with question details"""
        query = """
            SELECT 
                uli.*,
                COALESCE(q.title, uq.title) as title,
                COALESCE(q.difficulty, uq.difficulty) as difficulty,
                CASE 
                    WHEN uli.question_id IS NOT NULL THEN 'regular'
                    ELSE 'user'
                END as question_type
            FROM user_list_items uli
            LEFT JOIN questions q ON uli.question_id = q.id
            LEFT JOIN user_questions uq ON uli.user_question_id = uq.id
            WHERE uli.list_id = ?
            ORDER BY uli.created_at DESC
        """
        return self.execute_query(query, (list_id,))
    
    def get_list_item_by_id(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific list item"""
        query = """
            SELECT 
                uli.*,
                COALESCE(q.title, uq.title) as title,
                COALESCE(q.difficulty, uq.difficulty) as difficulty,
                CASE 
                    WHEN uli.question_id IS NOT NULL THEN 'regular'
                    ELSE 'user'
                END as question_type
            FROM user_list_items uli
            LEFT JOIN questions q ON uli.question_id = q.id
            LEFT JOIN user_questions uq ON uli.user_question_id = uq.id
            WHERE uli.id = ?
        """
        return self.execute_query_one(query, (item_id,))
    
    def update_item_status(self, item_id: int, status: str, notes: str = None) -> bool:
        """Update the status of a list item"""
        query = """
            UPDATE user_list_items 
            SET status = ?, notes = ?
            WHERE id = ?
        """
        return self.execute_update(query, (status, notes, item_id)) > 0
    
    def get_user_default_lists(self, user_id: int) -> Dict[str, int]:
        """Get default list IDs for a user"""
        query = """
            SELECT list_type, id 
            FROM user_lists 
            WHERE user_id = ? AND is_default = TRUE
        """
        results = self.execute_query(query, (user_id,))
        return {row['list_type']: row['id'] for row in results}
    
    def is_item_in_list(self, list_id: int, question_id: int = None, user_question_id: int = None) -> bool:
        """Check if an item is already in a list"""
        query = """
            SELECT 1 FROM user_list_items 
            WHERE list_id = ? AND 
                  ((question_id = ? AND question_id IS NOT NULL) OR 
                   (user_question_id = ? AND user_question_id IS NOT NULL))
        """
        return self.execute_query_one(query, (list_id, question_id, user_question_id)) is not None
