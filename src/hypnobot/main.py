import os
from typing import Dict, Any
import argparse
from dotenv import load_dotenv

from hypnobot.crew import HypnoCrew, HypnoChatProcess
from hypnobot.utils.logging import setup_logging, get_logger
from hypnobot.agents import ClientAgent, QAAgent
from hypnobot.tasks import ChatTask, ReviewTask

# Load environment variables from .env file
load_dotenv()

# Set up logging
setup_logging()
logger = get_logger(__name__)

def check_api_key() -> bool:
    """Check if the OpenAI API key is properly set.
    
    Returns:
        True if the API key seems valid, False otherwise.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable is not set")
        return False
    
    if api_key == "your_openai_api_key_here":
        logger.error("OPENAI_API_KEY is set to the default value from .env.example")
        return False
    
    # A very basic check for the key format
    if not api_key.startswith("sk-"):
        logger.warning("OPENAI_API_KEY does not start with 'sk-', might not be valid")
    
    return True

def check_default_configurations() -> Dict[str, bool]:
    """Check if any components are using default configurations.
    
    Returns:
        A dictionary mapping component names to whether they're using defaults.
    """
    client_agent = ClientAgent()
    qa_agent = QAAgent()
    chat_task = ChatTask()
    review_task = ReviewTask()
    
    return {
        "client_agent": client_agent.is_using_default_config(),
        "qa_agent": qa_agent.is_using_default_config(),
        "chat_task": chat_task.is_using_default_config(),
        "review_task": review_task.is_using_default_config(),
    }

def display_config_warnings():
    """Check for default configurations and display warnings if found."""
    default_configs = check_default_configurations()
    using_defaults = any(default_configs.values())
    
    if using_defaults:
        print("\n⚠️  WARNING: Some components are using default configurations:")
        for component, is_default in default_configs.items():
            if is_default:
                print(f"  - {component} is using default configuration")
        print("  This may affect the behavior of the chatbot.")
        print("  Check your YAML configuration files.\n")

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
    parser.add_argument(
        "--check-config", action="store_true", help="Check configuration status and exit"
    )
    
    args = parser.parse_args()
    
    # Check if OpenAI API key is set
    if not check_api_key():
        print("Error: OPENAI_API_KEY environment variable is not properly set.")
        print("Please set it in the .env file (based on .env.example) or as an environment variable.")
        print("NEVER commit your actual API key to the repository!")
        return 1
    
    # Check configuration if requested
    if args.check_config:
        default_configs = check_default_configurations()
        print("Configuration Status:")
        for component, is_default in default_configs.items():
            status = "Default" if is_default else "Custom (from YAML)"
            print(f"  {component}: {status}")
        return 0
    
    if args.interactive:
        # Interactive mode
        print("Hypnotherapy Chatbot - Interactive Mode")
        print("Type 'exit' or 'quit' to end the session.")
        
        # Display configuration warnings
        display_config_warnings()
        
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