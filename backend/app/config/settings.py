"""
Application configuration
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str = "devprep_problems.db"
    echo: bool = False


@dataclass
class AppConfig:
    """Application configuration"""
    title: str = "DevPrep Questions Browser API"
    version: str = "1.0.0"
    description: str = "API for browsing DevPrep questions with company and difficulty filtering"
    debug: bool = False
    cors_origins: list = None
    
    # Database
    database: DatabaseConfig = None
    
    def __post_init__(self):
        if self.database is None:
            self.database = DatabaseConfig()
        
        if self.cors_origins is None:
            self.cors_origins = ["http://localhost:3000", "http://127.0.0.1:3000","http://localhost:3001", "http://127.0.0.1:3001"]


# Global configuration instance
config = AppConfig(
    debug=os.getenv("DEBUG", "false").lower() == "true"
)
