#!/usr/bin/env python3
"""Script to check if the environment variables are properly set."""

import os
import sys
from dotenv import load_dotenv

def check_environment_mode():
    """Check if we're running in production or development mode."""
    env = os.environ.get("ENVIRONMENT", "development")
    is_production = env == "production"
    
    if is_production:
        print("✅ Running in production mode")
        print("   Environment variables should be set on the hosting platform")
    else:
        print("✅ Running in development mode")
        print("   Environment variables can be loaded from .env file")
    
    return is_production

def check_api_key(is_production):
    """Check if the OpenAI API key is set."""
    # Get API key directly from environment
    api_key = os.environ.get("OPENAI_API_KEY")
    
    # In development mode, try loading from .env if not found
    if not api_key and not is_production:
        print("   API key not found in environment variables, checking .env file")
        load_dotenv()
        api_key = os.environ.get("OPENAI_API_KEY")
    
    # Check if key exists
    if not api_key:
        if is_production:
            print("❌ OPENAI_API_KEY is not set in your environment variables")
            print("   In production, set this on your hosting platform")
        else:
            print("❌ OPENAI_API_KEY is not set in your environment or .env file")
            print("   Please create a .env file based on .env.example and add your API key")
        return False
    
    # Check for default value
    if api_key == "your_openai_api_key_here":
        print("❌ OPENAI_API_KEY is set to the default value in .env.example")
        print("   Please update it with your actual API key")
        return False
    
    # Simple format check (not foolproof)
    if not api_key.startswith("sk-"):
        print("⚠️  Warning: OPENAI_API_KEY does not start with 'sk-'")
        print("   This may not be a valid OpenAI API key")
    
    print("✅ OPENAI_API_KEY is set")
    return True

def check_env_file(is_production):
    """Check if the .env file exists."""
    if is_production:
        print("ℹ️  .env file not needed in production mode")
        return True
    
    if not os.path.exists(".env"):
        print("❌ .env file not found")
        print("   In development mode, please create a .env file based on .env.example")
        return False
    
    print("✅ .env file exists")
    return True

def main():
    """Check environment setup."""
    print("Checking environment setup...\n")
    
    is_production = check_environment_mode()
    print()
    
    env_file_ok = check_env_file(is_production)
    print()
    
    api_key_ok = check_api_key(is_production)
    
    if (is_production or env_file_ok) and api_key_ok:
        print("\n✅ Environment is properly set up")
        return 0
    else:
        print("\n❌ Environment setup issues found")
        print("   Please fix the issues above before running the application")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 