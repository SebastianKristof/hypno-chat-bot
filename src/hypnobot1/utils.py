"""
Utility functions for the HypnoBot1 system.
"""

import os
import logging
import yaml

def get_logger(name):
    """Create a logger with the given name."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def load_config(config_path, config_name):
    """Load configuration from a YAML file.
    
    Args:
        config_path: Path to the configuration directory
        config_name: Name of the configuration file (without .yaml extension)
        
    Returns:
        Dictionary containing the configuration or empty dict if file not found
    """
    try:
        file_path = os.path.join(config_path, f"{config_name}.yaml")
        with open(file_path, "r") as file:
            return yaml.safe_load(file) or {}
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Error loading configuration from {file_path}: {e}")
        return {}

def get_config_path():
    """Get the path to the configuration directory."""
    return os.path.join(os.path.dirname(__file__), "config") 