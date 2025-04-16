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
    # Model pricing per 1M tokens (as of 2025)
    model_pricing = {
        # Latest models
        "gpt-4.1": {"input": 2.00, "output": 8.00},
        "gpt-4.1-mini": {"input": 0.40, "output": 1.60},
        "gpt-4.1-nano": {"input": 0.10, "output": 0.40},
        "gpt-4.5-preview": {"input": 75.00, "output": 150.00},
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "o1": {"input": 15.00, "output": 60.00},
        "o1-pro": {"input": 150.00, "output": 600.00},
        "o3-mini": {"input": 1.10, "output": 4.40},
        "o1-mini": {"input": 1.10, "output": 4.40},
        
        # Legacy models
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "gpt-4": {"input": 30.00, "output": 60.00},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50}
    }
    
    # Default to gpt-4o-mini pricing if model is not in the list
    pricing = model_pricing.get(model_name, {"input": 0.15, "output": 0.60})
    
    # Calculate costs
    prompt_tokens = token_usage.get("prompt_tokens", 0)
    completion_tokens = token_usage.get("completion_tokens", 0)
    
    # Pricing is per 1M tokens, so divide by 1,000,000 (not 1,000)
    input_cost = (prompt_tokens / 1000000) * pricing["input"]
    output_cost = (completion_tokens / 1000000) * pricing["output"]
    total_cost = input_cost + output_cost
    
    logger.info(f"Cost calculation for {model_name}: {prompt_tokens} prompt tokens, {completion_tokens} completion tokens")
    logger.info(f"Using rates: ${pricing['input']}/1M input, ${pricing['output']}/1M output")
    logger.info(f"Calculated cost: ${input_cost:.6f} input + ${output_cost:.6f} output = ${total_cost:.6f} total")
    
    return {
        "total_cost": total_cost,
        "input_cost": input_cost,
        "output_cost": output_cost,
        "model": model_name,
        "pricing_rates": {
            "input_per_million": pricing["input"],
            "output_per_million": pricing["output"]
        },
        "tokens": {
            "prompt": prompt_tokens,
            "completion": completion_tokens,
            "total": token_usage.get("total_tokens", 0)
        }
    } 