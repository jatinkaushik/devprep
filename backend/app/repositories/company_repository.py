"""
Company repository for database operations
"""
from typing import List, Any, Optional
from app.repositories.base_repository import BaseRepository


class CompanyRepository(BaseRepository):
    """Repository for company-related database operations"""
    
    def find_all(self, **kwargs) -> List[Any]:
        """Find all companies"""
        query = "SELECT id, name FROM companies ORDER BY name"
        return self.execute_query(query)
    
    def find_by_id(self, id: int) -> Optional[Any]:
        """Find company by ID"""
        query = "SELECT id, name FROM companies WHERE id = ?"
        return self.execute_query_one(query, (id,))
    
    def find_by_name(self, name: str) -> Optional[Any]:
        """Find company by name"""
        query = "SELECT id, name FROM companies WHERE name = ?"
        return self.execute_query_one(query, (name,))
