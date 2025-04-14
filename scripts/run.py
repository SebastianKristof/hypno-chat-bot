#!/usr/bin/env python3
"""Run script for the hypnotherapy chatbot."""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.hypnobot.main import main

if __name__ == "__main__":
    sys.exit(main()) 