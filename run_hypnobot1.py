#!/usr/bin/env python3
"""
Run HypnoBot1 with sample messages.
This script demonstrates how to use HypnoBot1 programmatically.
"""

import os
import sys
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv(verbose=True)

# Make sure the API key is set in the environment
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("Error: OPENAI_API_KEY not found in environment variables or .env file.")
    print("Please check your .env file.")
    sys.exit(1)
elif "your_openai_api_key_here" in api_key:
    print("Error: OPENAI_API_KEY contains a placeholder value. Please update it in your .env file.")
    sys.exit(1)
else:
    print(f"API key found with length: {len(api_key)}")

# Add the src directory to the path
sys.path.insert(0, os.path.abspath("./"))

# Import the HypnoBot1Crew
from hypnobot1 import HypnoBot1Crew

def run_hypnobot1():
    """Run HypnoBot1 with a series of test messages."""
    print("\n" + "="*50)
    print("HypnoBot1 Demonstration")
    print("="*50)
    
    # Create the crew
    print("\nInitializing HypnoBot1...")
    hypnobot = HypnoBot1Crew()
    
    # Sample messages to process
    sample_messages = [
        "What is hypnotherapy?",
        "How does hypnotherapy work for anxiety?",
        "Can hypnotherapy help with weight loss?",
        "Is hypnotherapy safe for everyone?"
    ]
    
    # Process each message
    for i, message in enumerate(sample_messages):
        print(f"\n[Test {i+1}] Processing: \"{message}\"")
        print("-" * 50)
        
        try:
            # Process with actual API
            start_time = time.time()
            result = hypnobot.process_message(message)
            end_time = time.time()
            print(f"Processing time: {end_time - start_time:.2f} seconds")
            
            # Display the results
            print("\nOriginal Response:")
            print(f"  {result['original_response']}")
            
            print("\nFinal Response (after safety review):")
            print(f"  {result['final_response']}")
            
            print(f"\nSafety Level: {result['safety_level']}")
            
            # Show modifications if any
            if result.get('metadata', {}).get('modifications'):
                print("\nModifications:")
                print(f"  {result['metadata']['modifications']}")
            
            print("\n" + "="*50)
            
        except Exception as e:
            print(f"Error processing message: {str(e)}")
    
    print("\nDemonstration completed!")

if __name__ == "__main__":
    run_hypnobot1() 