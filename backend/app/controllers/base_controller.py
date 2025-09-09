"""
Base controller class
"""
from abc import ABC
from fastapi import HTTPException
from app.utils.logging import logger, log_exception


class BaseController(ABC):
    """Abstract base controller class"""
    
    def __init__(self):
        pass
    
    def handle_error(self, error: Exception, message: str = "An error occurred"):
        """Handle and transform errors to HTTP exceptions"""
        # Log the error
        log_exception(error, message)
        
        if isinstance(error, ValueError):
            logger.warning(f"Bad request: {str(error)}")
            raise HTTPException(status_code=400, detail=str(error))
        elif isinstance(error, FileNotFoundError):
            logger.warning(f"Not found: {str(error)}")
            raise HTTPException(status_code=404, detail=str(error))
        else:
            logger.error(f"Internal server error: {message} - {str(error)}")
            raise HTTPException(status_code=500, detail=message)
