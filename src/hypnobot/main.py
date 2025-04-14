import os
from typing import Dict, Any
import argparse
from dotenv import load_dotenv

from hypnobot.crew import HypnoCrew, HypnoChatProcess
from hypnobot.utils.logging import setup_logging, get_logger

# Load environment variables from .env file
load_dotenv()

# Set up logging
setup_logging()
logger = get_logger(__name__)

def process_message(message: str, use_process: bool = True) -> Dict[str, Any]:
    """Process a user message using the hypnotherapy chatbot.
    
    Args:
        message: The user's message text.
        use_process: Whether to use the Process approach (True) or
            the Crew approach (False).
            
    Returns:
        A dictionary containing the processing results.
    """
    logger.info(f"Processing message (use_process={use_process}): {message[:50]}...")
    
    try:
        if use_process:
            # Use the Process approach
            processor = HypnoChatProcess()
        else:
            # Use the Crew approach
            processor = HypnoCrew()
        
        # Process the message
        result = processor.process_message(message)
        
        logger.info(f"Processing complete. Safety level: {result.get('safety_level', 'unknown')}")
        return result
    
    except Exception as e:
        logger.error(f"Error in process_message: {str(e)}")
        return {
            "original_response": "",
            "final_response": "I apologize, but I encountered an issue processing your message. Please try again.",
            "safety_level": 2,
            "metadata": {"error": str(e)},
        }

def main():
    """Run the hypnotherapy chatbot as a command-line application."""
    parser = argparse.ArgumentParser(description="Hypnotherapy Chatbot")
    parser.add_argument("--message", "-m", type=str, help="Message to process")
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Run in interactive mode"
    )
    parser.add_argument(
        "--use-crew", action="store_true", help="Use Crew instead of Process"
    )
    
    args = parser.parse_args()
    
    # Check if OpenAI API key is set
    if not os.environ.get("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable is not set.")
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it in the .env file or as an environment variable.")
        return 1
    
    if args.interactive:
        # Interactive mode
        print("Hypnotherapy Chatbot - Interactive Mode")
        print("Type 'exit' or 'quit' to end the session.")
        
        while True:
            # Get user input
            user_input = input("\nYou: ")
            
            # Check for exit command
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            # Process the message
            result = process_message(user_input, not args.use_crew)
            
            # Display the result
            print(f"\nHypnoBot: {result['final_response']}")
            
            # Show safety level in debug mode
            if os.environ.get("DEBUG", "").lower() == "true":
                print(f"[Safety Level: {result.get('safety_level', 'unknown')}]")
    
    elif args.message:
        # Process a single message
        result = process_message(args.message, not args.use_crew)
        print(result["final_response"])
    
    else:
        # No input provided
        parser.print_help()
    
    return 0

if __name__ == "__main__":
    exit(main()) 