"""
Database connection management
"""
import sqlite3
import os
from contextlib import contextmanager
from typing import Generator
from app.config.settings import config
from app.utils.logging import logger, log_exception


class DatabaseManager:
    """Singleton database connection manager"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Use relative path from the backend directory
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.database_url = os.path.join(backend_dir, "devprep_problems.db")
        logger.info(f"Database initialized with path: {self.database_url}")
        # Check if the database file exists
        if not os.path.exists(self.database_url):
            logger.error(f"Database file not found at: {self.database_url}")
        else:
            logger.info(f"Database file exists at: {self.database_url}")
    
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get database connection with automatic cleanup"""
        try:
            logger.debug(f"Opening database connection to {self.database_url}")
            conn = sqlite3.connect(self.database_url)
            conn.row_factory = sqlite3.Row
            yield conn
        except sqlite3.Error as e:
            log_exception(e, f"Failed to connect to database at {self.database_url}")
            raise
        finally:
            if 'conn' in locals():
                logger.debug("Closing database connection")
                conn.close()
    
    def get_cursor(self, conn: sqlite3.Connection) -> sqlite3.Cursor:
        """Get cursor from connection"""
        return conn.cursor()


# Global database manager instance
db_manager = DatabaseManager()
