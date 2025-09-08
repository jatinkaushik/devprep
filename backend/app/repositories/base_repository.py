"""
Base repository class
"""
from abc import ABC, abstractmethod
from typing import Any, List, Optional, Dict
from app.utils.database import db_manager


class BaseRepository(ABC):
    """Abstract base repository class"""
    
    def __init__(self):
        self.db_manager = db_manager
    
    @abstractmethod
    def find_all(self, **kwargs) -> List[Any]:
        """Find all records matching criteria"""
        pass
    
    @abstractmethod
    def find_by_id(self, id: int) -> Optional[Any]:
        """Find record by ID"""
        pass
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute query and return results as dictionaries"""
        with self.db_manager.get_connection() as conn:
            cursor = self.db_manager.get_cursor(conn)
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_query_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Execute query and return single result"""
        with self.db_manager.get_connection() as conn:
            cursor = self.db_manager.get_cursor(conn)
            cursor.execute(query, params)
            result = cursor.fetchone()
            return dict(result) if result else None
