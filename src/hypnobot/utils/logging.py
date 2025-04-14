import logging
import os
import sys
from typing import Optional, Union

# Configure basic logging
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def setup_logging(
    level: Optional[Union[int, str]] = None,
    log_format: Optional[str] = None,
    log_file: Optional[str] = None,
) -> None:
    """Set up logging configuration for the application.
    
    Args:
        level: The logging level (e.g., logging.INFO, "INFO", etc.).
            If None, uses the LOG_LEVEL environment variable or DEFAULT_LOG_LEVEL.
        log_format: The format string for log messages.
            If None, uses DEFAULT_LOG_FORMAT.
        log_file: Path to a log file.
            If None, logs are sent to stderr.
    """
    # Determine log level
    if level is None:
        env_level = os.environ.get("LOG_LEVEL", "").upper()
        if env_level:
            level = getattr(logging, env_level, DEFAULT_LOG_LEVEL)
        else:
            level = DEFAULT_LOG_LEVEL
    elif isinstance(level, str):
        level = getattr(logging, level.upper(), DEFAULT_LOG_LEVEL)
    
    # Set up handlers
    handlers = []
    
    # Add file handler if log_file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        handlers.append(file_handler)
    
    # Always add a stream handler for console output
    stream_handler = logging.StreamHandler(sys.stderr)
    handlers.append(stream_handler)
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format=log_format or DEFAULT_LOG_FORMAT,
        handlers=handlers,
    )


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance.
    
    Args:
        name: The name of the logger, typically __name__.
        
    Returns:
        A configured Logger instance.
    """
    return logging.getLogger(name) 