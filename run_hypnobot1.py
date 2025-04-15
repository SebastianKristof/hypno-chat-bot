#!/usr/bin/env python3
"""
Run HypnoBot1 with sample messages or in interactive mode.
This script demonstrates how to use HypnoBot1 programmatically or as an interactive chatbot.
"""

import os
import sys
import argparse
from dotenv import load_dotenv, find_dotenv
import time

# Print diagnostic information
print("Current working directory:", os.getcwd())
print("Looking for .env file at:", find_dotenv())

# Load environment variables from .env file
load_dotenv(verbose=True)

# Check environment variables after loading
print("Environment variables after loading .env:")
api_key = os.environ.get("OPENAI_API_KEY")
print(f"OPENAI_API_KEY exists: {api_key is not None}")
if api_key:
    print(f"OPENAI_API_KEY length: {len(api_key)}")
    print(f"OPENAI_API_KEY first 10 chars: {api_key[:10]}...")
    print(f"OPENAI_API_KEY last 10 chars: {api_key[-10:]}...")

# Add the src directory to the path
sys.path.insert(0, os.path.abspath("./"))

# Import the HypnoBot1Crew
from hypnobot1 import HypnoBot1Crew

def run_demo():
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

def run_interactive():
    """Run HypnoBot1 in interactive mode, allowing the user to chat with it."""
    print("\n" + "="*50)
    print("HypnoBot1 Interactive Mode")
    print("="*50)
    print("Type 'exit', 'quit', or 'bye' to end the conversation.")
    print("Type 'clear' to start a new conversation.")
    print("Type 'help' to see these instructions again.")
    print("="*50)
    
    # Create the crew
    print("\nInitializing HypnoBot1...")
    try:
        hypnobot = HypnoBot1Crew()
        print("Initialization successful!")
    except Exception as e:
        print(f"Error initializing HypnoBot1: {e}")
        print("Check your API key and configuration files.")
        return
    
    # Start the conversation loop
    conversation_history = []
    user_name = input("\nWhat is your name? (Press Enter to remain anonymous): ").strip()
    if not user_name:
        user_name = "User"
    
    print(f"\nHello, {user_name}! How can I assist you with hypnotherapy today?")
    
    while True:
        # Get user input
        try:
            user_message = input("\nYou: ").strip()
        except KeyboardInterrupt:
            print("\n\nKeyboard interrupt detected. Exiting...")
            break
        except EOFError:
            print("\n\nEOF detected. Exiting...")
            break
        
        # Check for exit commands
        if user_message.lower() in ['exit', 'quit', 'bye']:
            print("\nThank you for chatting with HypnoBot1. Goodbye!")
            break
        
        # Check for help command
        if user_message.lower() == 'help':
            print("\n" + "="*50)
            print("HypnoBot1 Interactive Mode Commands:")
            print("- Type 'exit', 'quit', or 'bye' to end the conversation.")
            print("- Type 'clear' to start a new conversation.")
            print("- Type 'help' to see these instructions.")
            print("="*50)
            continue
        
        # Check for clear command
        if user_message.lower() == 'clear':
            conversation_history = []
            print("\nConversation cleared. Starting a new session.")
            continue
        
        # Skip empty messages
        if not user_message:
            print("Please type a message or 'exit' to quit.")
            continue
        
        try:
            # Process with actual API
            print("\nProcessing your message... This may take a moment.")
            spinner = ['|', '/', '-', '\\']
            start_time = time.time()
            
            # Process the message
            result = hypnobot.process_message(user_message, user_name)
            processing_time = time.time() - start_time
            
            # Display processing time
            print(f"(Response generated in {processing_time:.1f} seconds)")
            
            # Display only the final response in interactive mode
            print(f"\nHypnoBot1: {result['final_response']}")
            
            # Optionally show safety level for transparency
            safety_level = result.get('safety_level', 0)
            if safety_level > 0:
                print(f"\n[Note: Response was reviewed for safety (level {safety_level}/4)]")
            
            # Add to conversation history
            conversation_history.append({
                "user": user_message,
                "bot": result['final_response']
            })
            
        except KeyboardInterrupt:
            print("\n\nProcessing interrupted. Ready for a new message.")
            continue
        except Exception as e:
            print(f"\nHypnoBot1: I apologize, but I encountered an issue processing your message: {str(e)}")
            print("Please try again or type 'exit' to quit.")
            # Log the error for debugging
            import traceback
            print("\nDebug information for developers:")
            traceback.print_exc()

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Run HypnoBot1 in demo or interactive mode')
    parser.add_argument('-i', '--interactive', action='store_true', help='Run in interactive mode')
    args = parser.parse_args()
    
    if args.interactive:
        run_interactive()
    else:
        run_demo() 