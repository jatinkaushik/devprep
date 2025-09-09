"""
Logging utilities for the application
"""
import os
import logging
from logging.handlers import RotatingFileHandler
import traceback
import inspect

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs")
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Configure logging
logger = logging.getLogger("devprep")
logger.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_format)
logger.addHandler(console_handler)

# File handler - main log file
file_handler = RotatingFileHandler(
    os.path.join(logs_dir, "devprep.log"),
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setLevel(logging.DEBUG)
file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_format)
logger.addHandler(file_handler)

# File handler - error log file
error_handler = RotatingFileHandler(
    os.path.join(logs_dir, "error.log"),
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
error_handler.setLevel(logging.ERROR)
error_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d')
error_handler.setFormatter(error_format)
logger.addHandler(error_handler)


def log_context():
    """Get the calling context information (file, function, line)"""
    frame = inspect.currentframe().f_back.f_back
    info = inspect.getframeinfo(frame)
    return f"{os.path.basename(info.filename)}:{info.function}:{info.lineno}"


def log_exception(e, message=None):
    """Log exception with traceback and context"""
    ctx = log_context()
    error_msg = f"{message}: {str(e)}" if message else str(e)
    logger.error(f"[{ctx}] {error_msg}")
    logger.error(f"[{ctx}] Traceback: {traceback.format_exc()}")
    return error_msg
