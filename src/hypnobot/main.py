import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the system path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from src.hypnobot.v2.hypnobot import HypnoBot

def main():
    """Main function to run the HypnoBot."""
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment variables.")
        print("Please set your OpenAI API key before running the bot.")
        print("You can create a .env file based on .env.example")
        return

    print("HypnoBot v2 - Hypnotherapy Chatbot")
    print("Type 'exit' to quit the chat")
    print("-" * 50)
    
    try:
        # Initialize the bot
        print("Initializing HypnoBot...")
        bot = HypnoBot()
        print("Initialization complete.")
        
        while True:
            # Get user input
            user_input = input("\nYou: ")
            
            # Check for exit command
            if user_input.lower() in ('exit', 'quit', 'bye'):
                print("HypnoBot: Goodbye! Take care.")
                break
            
            # Process the input
            try:
                print("Processing your request...")
                response = bot.process_input(user_input)
                print(f"\nHypnoBot: {response}")
            except Exception as e:
                print(f"\nError: {str(e)}")
                print("HypnoBot: I'm sorry, I encountered an error processing your request.")
    except Exception as e:
        print(f"Error initializing HypnoBot: {str(e)}")
        print("Please check your API key and dependencies.")

if __name__ == "__main__":
    main() 