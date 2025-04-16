"""
Utility functions for the HypnoBot1 system.
"""

import os
import logging
import yaml
from typing import Dict, Any, Optional

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    logger = logging.getLogger(name)
    
    # If the logger already has handlers, return it
    if logger.handlers:
        return logger
    
    # Configure logging
    logger.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # Add the handlers to the logger
    logger.addHandler(console_handler)
    
    return logger

def get_config_path() -> str:
    """Get the path to the configuration files directory."""
    # Construct the path to the 'config' directory relative to this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "config")
    
    return config_path

def load_config(config_dir: str, config_name: str) -> Dict[str, Any]:
    """Load configuration from a YAML file.
    
    Args:
        config_dir: Directory containing configuration files
        config_name: Name of the configuration file (without extension)
        
    Returns:
        Dictionary containing the configuration
    """
    logger = get_logger(__name__)
    
    # Construct the full path to the configuration file
    config_file = os.path.join(config_dir, f"{config_name}.yaml")
    
    # Check if the file exists
    if not os.path.exists(config_file):
        logger.warning(f"Configuration file not found: {config_file}")
        return {}
    
    # Load the YAML file
    try:
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
        
        if not config:
            logger.warning(f"Empty configuration file: {config_file}")
            return {}
            
        return config
    except Exception as e:
        logger.error(f"Error loading configuration from {config_file}: {e}")
        return {}

def calculate_cost(token_usage: Dict[str, int], model_name: str = "gpt-4o-mini") -> Dict[str, float]:
    """Calculate the cost of tokens used.
    
    Args:
        token_usage: Dictionary with token usage statistics
        model_name: Name of the model used for pricing
        
    Returns:
        Dictionary with cost information
    """
    # Model pricing per 1000 tokens (as of May 2024)
    model_pricing = {
        "gpt-4o-mini": {"input": 0.15, "output": 0.6},
        "gpt-4o": {"input": 5.0, "output": 15.0},
        "gpt-4-turbo": {"input": 10.0, "output": 30.0},
        "gpt-4": {"input": 30.0, "output": 60.0},
        "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
    }
    
    # Default to gpt-4o-mini pricing if model is not in the list
    pricing = model_pricing.get(model_name, {"input": 0.15, "output": 0.6})
    
    # Calculate costs
    prompt_tokens = token_usage.get("prompt_tokens", 0)
    completion_tokens = token_usage.get("completion_tokens", 0)
    
    input_cost = (prompt_tokens / 1000) * pricing["input"]
    output_cost = (completion_tokens / 1000) * pricing["output"]
    total_cost = input_cost + output_cost
    
    return {
        "total_cost": total_cost,
        "input_cost": input_cost,
        "output_cost": output_cost,
        "model": model_name,
        "tokens": {
            "prompt": prompt_tokens,
            "completion": completion_tokens,
            "total": token_usage.get("total_tokens", 0)
        }
    } 