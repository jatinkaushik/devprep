"""
Database configuration and connection management
"""
import sqlite3
import os
from contextlib import contextmanager
from typing import Generator


DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'devprep_problems.db')


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """
    Get database connection with proper cleanup
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()


def init_database():
    """
    Initialize database with required tables
    """
    with get_db_connection() as conn:
        # Database is already initialized
        # This function can be used for future migrations
        pass
