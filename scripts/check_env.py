#!/usr/bin/env python3
"""Script to check if the environment variables are properly set."""

import os
import sys
from dotenv import load_dotenv

def check_api_key():
    """Check if the OpenAI API key is set."""
    # Load environment variables
    load_dotenv()
    
    # Check if OPENAI_API_KEY is set
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY is not set in your environment")
        print("Please create a .env file based on .env.example and add your API key")
        return False
    
    if api_key == "your_openai_api_key_here":
        print("❌ OPENAI_API_KEY is set to the default value in .env.example")
        print("Please update it with your actual API key")
        return False
    
    # Simple format check (not foolproof)
    if not api_key.startswith("sk-"):
        print("⚠️  Warning: OPENAI_API_KEY does not start with 'sk-'")
        print("This may not be a valid OpenAI API key")
    
    print("✅ OPENAI_API_KEY is set")
    return True

def check_env_file():
    """Check if the .env file exists."""
    if not os.path.exists(".env"):
        print("❌ .env file not found")
        print("Please create a .env file based on .env.example")
        return False
    
    print("✅ .env file exists")
    return True

def main():
    """Check environment setup."""
    print("Checking environment setup...\n")
    
    env_file_ok = check_env_file()
    api_key_ok = check_api_key()
    
    if env_file_ok and api_key_ok:
        print("\n✅ Environment is properly set up")
        return 0
    else:
        print("\n❌ Environment setup issues found")
        print("Please fix the issues above before running the application")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 