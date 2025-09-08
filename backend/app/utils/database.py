"""
Database connection management
"""
import sqlite3
from contextlib import contextmanager
from typing import Generator
from app.config.settings import config


class DatabaseManager:
    """Singleton database connection manager"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        import os
        # Use relative path from the backend directory
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.database_url = os.path.join(backend_dir, "devprep_problems.db")
    
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get database connection with automatic cleanup"""
        conn = sqlite3.connect(self.database_url)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def get_cursor(self, conn: sqlite3.Connection) -> sqlite3.Cursor:
        """Get cursor from connection"""
        return conn.cursor()


# Global database manager instance
db_manager = DatabaseManager()
