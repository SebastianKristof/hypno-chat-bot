#!/usr/bin/env python3
"""Test configuration loading for the hypnotherapy chatbot."""

import os
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_environment_variables():
    """Print the environment variables used by the application."""
    print("Environment Variables:")
    print(f"  OPENAI_API_KEY: {'Set' if os.environ.get('OPENAI_API_KEY') else 'Not Set'}")
    print(f"  DEBUG: {os.environ.get('DEBUG', 'Not Set')}")
    print(f"  LOG_LEVEL: {os.environ.get('LOG_LEVEL', 'Not Set')}")
    print(f"  VECTOR_DB_PATH: {os.environ.get('VECTOR_DB_PATH', 'Not Set')}")
    print(f"  SAFETY_THRESHOLD: {os.environ.get('SAFETY_THRESHOLD', 'Not Set')}")

def print_yaml_config(config_path):
    """Print the contents of a YAML configuration file."""
    try:
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
            print(f"\nConfiguration from {config_path}:")
            print(f"  Keys: {list(config.keys())}")
            for key, value in config.items():
                print(f"  {key}: {type(value).__name__}")
    except Exception as e:
        print(f"\nError loading {config_path}: {e}")

def main():
    """Run the configuration test."""
    print("Hypnotherapy Chatbot Configuration Test\n")
    
    # Check environment variables
    print_environment_variables()
    
    # Check YAML configuration files
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.join(base_dir, "config")
    
    # Check if config directory exists
    if not os.path.exists(config_dir):
        print(f"\nConfig directory not found: {config_dir}")
        return
    
    # Check agent configuration
    agents_config_path = os.path.join(config_dir, "agents.yaml")
    print_yaml_config(agents_config_path)
    
    # Check task configuration
    tasks_config_path = os.path.join(config_dir, "tasks.yaml")
    print_yaml_config(tasks_config_path)
    
    # Check safety rules configuration
    safety_config_path = os.path.join(config_dir, "safety_rules.yaml")
    print_yaml_config(safety_config_path)

if __name__ == "__main__":
    main() 