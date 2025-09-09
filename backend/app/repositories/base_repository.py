"""
Base repository class
"""
from abc import ABC, abstractmethod
from typing import Any, List, Optional, Dict
from app.utils.database import db_manager
from app.utils.logging import logger, log_exception


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
        try:
            logger.debug(f"Executing query: {query}")
            logger.debug(f"Parameters: {params}")
            with self.db_manager.get_connection() as conn:
                cursor = self.db_manager.get_cursor(conn)
                cursor.execute(query, params)
                results = [dict(row) for row in cursor.fetchall()]
                logger.debug(f"Query returned {len(results)} results")
                return results
        except Exception as e:
            log_exception(e, f"Database query error")
            raise
    
    def execute_query_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Execute query and return single result"""
        try:
            logger.debug(f"Executing query (one): {query}")
            logger.debug(f"Parameters: {params}")
            with self.db_manager.get_connection() as conn:
                cursor = self.db_manager.get_cursor(conn)
                cursor.execute(query, params)
                result = cursor.fetchone()
                logger.debug(f"Query returned: {result is not None}")
                return dict(result) if result else None
        except Exception as e:
            log_exception(e, f"Database query_one error")
            raise
