import logging
import os
from datetime import datetime

class LoggerSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LoggerSingleton, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.logger = logging.getLogger("connectly_logger")
        
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        # File handler for all logs
        file_handler = logging.FileHandler(
            f'logs/connectly_{datetime.now().strftime("%Y%m%d")}.log'
        )
        
        # Console handler for error logs
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        
        # Create formatters and add it to the handlers
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(name)s:%(lineno)d] - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)
        
        # Add handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Set logging level
        self.logger.setLevel(logging.INFO)

    def get_logger(self):
        return self.logger
        
    def log_api_request(self, request, response=None):
        """Log API request details"""
        log_data = {
            'method': request.method,
            'path': request.path,
            'user': str(request.user),
            'ip': request.META.get('REMOTE_ADDR'),
        }
        
        if response:
            log_data['status'] = response.status_code
            
        self.logger.info(f"API Request: {log_data}")
        
    def log_error(self, error, context=None):
        """Log error with context"""
        error_msg = f"Error: {str(error)}"
        if context:
            error_msg += f" Context: {context}"
        self.logger.error(error_msg)
