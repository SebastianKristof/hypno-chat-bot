#!/usr/bin/env python3

"""
Test script for the HypnoBot implementation to verify CrewAI integration fixes.
This script directly tests the HypnoBot class without going through the API.
"""

import os
import sys
from pathlib import Path
import traceback

# Add the project root to the system path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

def main():
    """Main test function"""
    print("HypnoBot Test Script")
    
    # Apply memory patch and CrewAI bug fixes
    print("\n1. Applying patches...")
    from src.hypnobot.memory_patch import patch_memory, patch_crew_ai_bugs
    patch_memory()
    patch_crew_ai_bugs()
    
    # Import the HypnoBot class
    print("\n2. Importing HypnoBot...")
    try:
        from src.hypnobot.v2.hypnobot import HypnoBot
        print("✅ Successfully imported HypnoBot")
    except Exception as e:
        print(f"❌ Error importing HypnoBot: {e}")
        print(traceback.format_exc())
        return 1
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ OPENAI_API_KEY environment variable not set")
        print("Please set your API key and try again:")
        print("export OPENAI_API_KEY=your_key_here")
        return 1
    
    # Create HypnoBot instance
    print("\n3. Creating HypnoBot instance...")
    try:
        bot = HypnoBot()
        print("✅ Successfully created HypnoBot instance")
    except Exception as e:
        print(f"❌ Error creating HypnoBot: {e}")
        print(traceback.format_exc())
        return 1
    
    # Test with a simple query
    print("\n4. Testing with a simple query...")
    try:
        test_input = "What is hypnotherapy good for?"
        print(f"Input: '{test_input}'")
        
        response = bot.process_input(test_input)
        print("\nResponse:")
        print("-" * 60)
        print(response)
        print("-" * 60)
        print("✅ Successfully processed query")
    except Exception as e:
        print(f"❌ Error processing query: {e}")
        print(traceback.format_exc())
        return 1
    
    print("\nAll tests completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 