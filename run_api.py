#!/usr/bin/env python3
"""
Script to run the HypnoBot API server.
"""
import os
import sys
import uvicorn
import argparse
import traceback
from pathlib import Path

# Add the project root to system path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

# Apply memory patch before importing any crewai modules
try:
    print("Applying memory patch...")
    from src.hypnobot.memory_patch import patch_memory
    if patch_memory():
        print("✅ Successfully applied memory patch")
    else:
        print("⚠️  Memory patch applied but returned False")
except ImportError as e:
    print(f"⚠️  Warning: Could not import memory_patch module: {e}")
    traceback.print_exc()
except Exception as e:
    print(f"⚠️  Warning: Failed to apply memory patch: {e}")
    traceback.print_exc()

# Test import of HypnoBot
try:
    print("Testing import of HypnoBot...")
    from src.hypnobot.v2 import HypnoBot
    print(f"✅ Successfully imported HypnoBot from src.hypnobot.v2")
except ImportError as e:
    print(f"❌ Failed to import HypnoBot: {e}")
    traceback.print_exc()
    
    # Try alternative import path
    try:
        print("Trying alternative import path...")
        from src.hypnobot.v2.hypnobot import HypnoBot
        print(f"✅ Successfully imported HypnoBot from src.hypnobot.v2.hypnobot")
    except ImportError as e:
        print(f"❌ Failed to import HypnoBot from alternative path: {e}")
        traceback.print_exc()
except Exception as e:
    print(f"❌ Unexpected error importing HypnoBot: {e}")
    traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the HypnoBot API server')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to run the server on')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload for development')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    print(f"📡 Starting HypnoBot API server at http://{args.host}:{args.port}")
    print("📚 API documentation available at /docs")
    
    # Run the app with the specified options
    log_level = "debug" if args.debug else "info"
    uvicorn.run(
        "src.hypnobot.api:app", 
        host=args.host, 
        port=args.port, 
        reload=args.reload,
        log_level=log_level
    ) 