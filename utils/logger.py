import logging
import os
from logging.handlers import RotatingFileHandler
from .config_manager import load_config
from datetime import datetime

class Logger:
    _instance = None

    def __init__(self):
        Logger._instance = self._setup_logger()  # Store logger in class variable

    def _setup_logger(self, name: str = 'cdli-json-export-processor-app', log_level=logging.INFO) -> logging.Logger:
        """Enhanced logger setup that respects config settings"""
        # Check config first
        config = load_config()
        if not config.get('logging_enabled', False):
            null_logger = logging.getLogger('null')
            null_logger.addHandler(logging.NullHandler())
            return null_logger
            
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Generate timestamped log filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = f'logs/{name}_{timestamp}.log'
        
        logger = logging.getLogger(name)
        logger.setLevel(log_level)
        
        # Remove existing handlers to prevent duplicates
        logger.handlers.clear()
        
        # File handler with rotation
        file_handler = RotatingFileHandler(log_file)
        
        # Detailed formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s'
        )
        
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Optional console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger

    @classmethod
    def get_logger(cls):
        if cls._instance is None:
            Logger()  # Creates instance and sets _instance
        return cls._instance

# Create singleton instance
logger = Logger.get_logger()