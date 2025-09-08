"""
Base controller class
"""
from abc import ABC
from fastapi import HTTPException


class BaseController(ABC):
    """Abstract base controller class"""
    
    def __init__(self):
        pass
    
    def handle_error(self, error: Exception, message: str = "An error occurred"):
        """Handle and transform errors to HTTP exceptions"""
        if isinstance(error, ValueError):
            raise HTTPException(status_code=400, detail=str(error))
        elif isinstance(error, FileNotFoundError):
            raise HTTPException(status_code=404, detail=str(error))
        else:
            raise HTTPException(status_code=500, detail=message)
