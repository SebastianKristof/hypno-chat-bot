#!/usr/bin/env python3
"""
Script to run the HypnoBot in CLI mode.
"""
import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()

# Add the project root to the system path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

try:
    from src.hypnobot.hypnobot import HypnoBot
    print("Successfully imported HypnoBot")
except ImportError as e:
    print(f"Error importing HypnoBot: {str(e)}")
    print(traceback.format_exc())
    sys.exit(1)

def main():
    """Main function to run the HypnoBot CLI."""
    parser = argparse.ArgumentParser(description='Run the HypnoBot in CLI mode')
    parser.add_argument('--model', type=str, help='OpenAI model to use (default: from env or gpt-3.5-turbo)')
    parser.add_argument('--single', '-s', type=str, help='Process a single message and exit')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--debug', '-d', action='store_true', help='Show full error traceback for debugging')
    
    args = parser.parse_args()
    
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment variables.")
        print("Please set your OpenAI API key before running the bot.")
        print("You can create a .env file based on .env.example")
        return 1
    
    try:
        # Initialize the bot with specified model if provided
        bot = HypnoBot(model_name=args.model)
        
        # Set verbosity
        if args.verbose:
            print(f"Using model: {bot.model_name}")
            print("Bot initialized successfully")
        
        # Single message mode
        if args.single:
            try:
                response = bot.process_input(args.single)
                print(f"\n{response}")
                return 0
            except Exception as e:
                print(f"\nError processing input: {str(e)}")
                if args.debug:
                    traceback.print_exc()
                return 1
        
        # Interactive mode
        print("HypnoBot v2 - Hypnotherapy Chatbot")
        print("Type 'exit' to quit the chat")
        print("-" * 50)
        
        while True:
            # Get user input
            user_input = input("\nYou: ")
            
            # Check for exit command
            if user_input.lower() in ('exit', 'quit', 'bye'):
                print("HypnoBot: Goodbye! Take care.")
                break
            
            # Process the input
            try:
                response = bot.process_input(user_input)
                print(f"\nHypnoBot: {response}")
            except Exception as e:
                print(f"\nError: {str(e)}")
                if args.debug:
                    traceback.print_exc()
                print("HypnoBot: I'm sorry, I encountered an error processing your request.")
        
        return 0
        
    except Exception as e:
        print(f"Error initializing bot: {str(e)}")
        if args.debug:
            traceback.print_exc()
        
        # Provide specific guidance based on the error
        if "supports_stop_words" in str(e):
            print("\nThere appears to be a compatibility issue between crewai and langchain_openai.")
            print("To fix this, try installing compatible versions:")
            print("pip install crewai==0.28.8 langchain-openai==0.0.2")
        
        return 1

if __name__ == "__main__":
    sys.exit(main()) 