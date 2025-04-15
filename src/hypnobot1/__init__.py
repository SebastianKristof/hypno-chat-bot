"""
HypnoBot1 - A hypnotherapy chatbot using CrewAI.
"""

import os
import sys
from dotenv import load_dotenv, find_dotenv
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Find the .env file
dotenv_path = find_dotenv()
logger.info(f"Looking for .env file at: {dotenv_path}")

# Load environment variables from .env file when the module is imported
# This ensures the API key is available to all HypnoBot1 components
if dotenv_path:
    logger.info(f"Loading environment variables from: {dotenv_path}")
    load_dotenv(dotenv_path=dotenv_path, override=True)
    logger.info("Environment variables loaded")
else:
    logger.warning("No .env file found. Using existing environment variables.")

# Check if the API key is available
api_key = os.environ.get("OPENAI_API_KEY")
if api_key:
    logger.info(f"OPENAI_API_KEY found with length: {len(api_key)}")
    
    # Check for project-style keys which might have special handling
    if api_key.startswith("sk-proj-"):
        logger.warning("Using a project-style API key (starts with sk-proj-)")
else:
    logger.warning("OPENAI_API_KEY not found in environment variables")

from hypnobot1.crew import HypnoBot1Crew

__all__ = ["HypnoBot1Crew"] 