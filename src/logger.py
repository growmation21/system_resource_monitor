"""
Logging configuration for System Resource Monitor

Provides centralized logging setup with file and console output,
configurable log levels, and rotation.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime

def setup_logging(level=logging.INFO, log_dir=None, max_bytes=10*1024*1024, backup_count=5):
    """
    Set up logging configuration
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files (default: ./logs)
        max_bytes: Maximum size of log file before rotation (default: 10MB)
        backup_count: Number of backup log files to keep (default: 5)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    
    # Create logs directory if not specified
    if log_dir is None:
        log_dir = Path(__file__).parent.parent / 'logs'
    else:
        log_dir = Path(log_dir)
    
    log_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger('system_monitor')
    logger.setLevel(level)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-15s | %(filename)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    log_file = log_dir / f'system_monitor_{datetime.now().strftime("%Y%m%d")}.log'
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)  # Always log DEBUG and above to file
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Error handler for critical errors
    error_log_file = log_dir / 'errors.log'
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_handler)
    
    # Log startup message
    logger.info("=" * 60)
    logger.info("System Resource Monitor - Logging Initialized")
    logger.info(f"Log Level: {logging.getLevelName(level)}")
    logger.info(f"Log Directory: {log_dir}")
    logger.info(f"Log File: {log_file}")
    logger.info("=" * 60)
    
    return logger

def get_logger(name=None):
    """
    Get a logger instance
    
    Args:
        name: Logger name (default: system_monitor)
    
    Returns:
        logging.Logger: Logger instance
    """
    if name is None:
        name = 'system_monitor'
    
    return logging.getLogger(name)
