"""
HypnoBot1 - A hypnotherapy chatbot using CrewAI.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file when the module is imported
# This ensures the API key is available to all HypnoBot1 components
load_dotenv(override=True)

from hypnobot1.crew import HypnoBot1Crew

__all__ = ["HypnoBot1Crew"] 