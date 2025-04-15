#!/usr/bin/env python3
"""
Interactive HypnoBot1 Chat Script

This script provides an interactive chat interface for HypnoBot1,
allowing users to have a conversation with the hypnotherapy chatbot.
"""

import os
import sys
from dotenv import load_dotenv
import time
import re

# Load environment variables
load_dotenv()

# Add the src directory to the path
sys.path.insert(0, os.path.abspath("./"))

# Import the HypnoBot1Crew
from hypnobot1 import HypnoBot1Crew

# ANSI color codes for terminal output
COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "green": "\033[32m",
    "blue": "\033[34m",
    "cyan": "\033[36m",
    "yellow": "\033[33m",
    "red": "\033[31m",
    "magenta": "\033[35m"
}

def print_colored(text, color="reset", end="\n"):
    """Print text with specified color."""
    print(f"{COLORS.get(color, '')}{text}{COLORS['reset']}", end=end)

def print_header():
    """Print the welcome header."""
    print("\n" + "="*70)
    print_colored("  HypnoBot1 - Interactive Hypnotherapy Chatbot", "cyan")
    print("="*70)
    print("\nWelcome to HypnoBot1, your AI hypnotherapy information assistant.")
    print("Ask questions about hypnotherapy or type 'exit' to quit.")
    print("Type 'help' for more commands.\n")
    print("-"*70)

def print_help():
    """Print help information."""
    print("\nAvailable commands:")
    print_colored("  help", "yellow", end=" - ")
    print("Show this help message")
    print_colored("  exit/quit", "yellow", end=" - ")
    print("Exit the program")
    print_colored("  clear", "yellow", end=" - ")
    print("Clear the screen")
    print_colored("  info", "yellow", end=" - ")
    print("Show information about the last response")
    print_colored("  debug [on/off]", "yellow", end=" - ")
    print("Toggle debug mode to see safety levels and modifications")
    print("-"*70 + "\n")

def clear_screen():
    """Clear the terminal screen."""
    # Use cls on Windows, clear on Unix/Linux/MacOS
    os.system('cls' if os.name == 'nt' else 'clear')

def simulate_response(message):
    """Simulate a response when no API key is available."""
    time.sleep(1)  # Simulate thinking
    
    # Some predefined responses
    if re.search(r'what\s+is\s+hypno(therapy|sis)', message, re.IGNORECASE):
        return {
            "original_response": "Hypnotherapy is a therapeutic technique that uses guided relaxation and focused attention to achieve a heightened state of awareness. In this state, a person is more open to suggestion and change.",
            "final_response": "Hypnotherapy is a therapeutic technique that uses guided relaxation and focused attention to achieve a heightened state of awareness. In this state, a person is more open to suggestion and change. It's important to note that results vary from person to person.",
            "safety_level": 0,
            "metadata": {
                "modifications": "Added a disclaimer about individual results varying.",
                "reasoning": "The original response is accurate but should include a note about varying results."
            }
        }
    elif re.search(r'anxiety|stress|worry', message, re.IGNORECASE):
        return {
            "original_response": "Hypnotherapy works for anxiety by helping you reach a deeply relaxed state where your mind becomes more receptive to positive suggestions. The therapist guides you to address anxious thoughts and replace them with calmer perspectives.",
            "final_response": "Hypnotherapy can help with anxiety by guiding you to a deeply relaxed state where your mind may become more receptive to positive suggestions. A hypnotherapist might help you explore anxious thoughts and consider calmer perspectives. However, results vary by individual, and hypnotherapy works best as a complementary approach alongside professionally recommended treatments for anxiety.",
            "safety_level": 1,
            "metadata": {
                "modifications": "Added qualifiers about effectiveness and recommended it as a complementary approach rather than a standalone treatment.",
                "reasoning": "The original response needed to be more cautious about therapeutic claims."
            }
        }
    elif re.search(r'weight|diet|eating|food', message, re.IGNORECASE):
        return {
            "original_response": "Yes, hypnotherapy can be effective for weight loss by addressing unconscious eating habits and motivations. It can help reprogram your mind to desire healthier foods and maintain motivation for exercise.",
            "final_response": "Hypnotherapy may be used as a complementary approach for weight management by exploring unconscious eating patterns and potentially enhancing motivation. However, scientific evidence for its effectiveness is mixed, and results vary significantly between individuals. Any weight loss program should include healthy eating, regular physical activity, and consultation with healthcare providers.",
            "safety_level": 2,
            "metadata": {
                "modifications": "Significantly revised to avoid making unsupported claims and added necessary medical context.",
                "reasoning": "The original response made claims about effectiveness that weren't sufficiently qualified."
            }
        }
    elif re.search(r'safe|danger|risk', message, re.IGNORECASE):
        return {
            "original_response": "Hypnotherapy is generally safe for most people when conducted by a qualified professional. However, it's not recommended for individuals with certain psychiatric conditions like psychosis or some personality disorders.",
            "final_response": "Hypnotherapy is generally considered safe for most people when conducted by a qualified professional. However, it's not recommended for everyone. People with certain conditions such as psychosis, some personality disorders, or severe mental health issues should consult with their healthcare provider before considering hypnotherapy. It's always important to work with licensed practitioners and inform them of your complete medical history.",
            "safety_level": 1,
            "metadata": {
                "modifications": "Expanded safety warnings and added recommendation to consult healthcare providers.",
                "reasoning": "The safety implications required more thorough explanation."
            }
        }
    else:
        # Generic response for other queries
        return {
            "original_response": f"I understand you're asking about {message[:20]}... This relates to hypnotherapy, which is a therapeutic technique that uses guided relaxation and focused attention.",
            "final_response": f"I understand you're asking about {message[:20]}... This relates to hypnotherapy, which is a therapeutic technique that uses guided relaxation and focused attention. For specific advice, it's best to consult with a qualified hypnotherapist or healthcare provider.",
            "safety_level": 0,
            "metadata": {
                "modifications": "Added recommendation to consult professionals.",
                "reasoning": "Added professional consultation recommendation for safety."
            }
        }

def run_interactive_chat():
    """Run an interactive chat session with HypnoBot1."""
    print_header()
    
    # Create the crew
    print_colored("Initializing HypnoBot1...", "blue")
    try:
        hypnobot = HypnoBot1Crew()
        print_colored("HypnoBot1 is ready!", "green")
    except Exception as e:
        print_colored(f"Error initializing HypnoBot1: {str(e)}", "red")
        print("Exiting...")
        return
    
    # Check API key
    api_key = os.environ.get("OPENAI_API_KEY", "")
    using_simulation = not api_key or "sk-proj-" in api_key or "your_" in api_key
    
    if using_simulation:
        print_colored("\nNote: Using simulated responses (no valid API key found)", "yellow")
        print("For full functionality, add your OpenAI API key to the .env file.")
    
    # Interactive loop variables
    last_response = None
    debug_mode = False
    
    # Main interaction loop
    while True:
        # Get user input
        print()
        try:
            user_input = input(f"{COLORS['bold']}You:{COLORS['reset']} ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break
        
        # Process commands
        user_input = user_input.strip()
        if not user_input:
            continue
            
        # Handle special commands
        if user_input.lower() in ['exit', 'quit']:
            print_colored("Goodbye!", "green")
            break
        elif user_input.lower() == 'help':
            print_help()
            continue
        elif user_input.lower() == 'clear':
            clear_screen()
            print_header()
            continue
        elif user_input.lower() == 'info' and last_response:
            print("\n" + "-"*50)
            print_colored("Last Response Information:", "cyan")
            print(f"Safety Level: {last_response['safety_level']}")
            if 'metadata' in last_response and last_response.get('metadata'):
                print("\nMetadata:")
                for key, value in last_response['metadata'].items():
                    if key == 'review_result':
                        print(f"\nFull Review: {value[:100]}...")
                    elif key == 'modifications':
                        print(f"Modifications: {value}")
                    elif key == 'reasoning':
                        print(f"Reasoning: {value}")
            print("-"*50)
            continue
        elif user_input.lower().startswith('debug'):
            parts = user_input.lower().split()
            if len(parts) > 1:
                debug_mode = parts[1] in ['on', 'true', '1', 'yes']
            else:
                debug_mode = not debug_mode
            print_colored(f"Debug mode: {'ON' if debug_mode else 'OFF'}", "yellow")
            continue
        
        # Process the user message
        print_colored("HypnoBot1 is thinking...", "blue")
        try:
            if using_simulation:
                result = simulate_response(user_input)
            else:
                result = hypnobot.process_message(user_input)
                
            # Store the response
            last_response = result
            
            # Print the bot's response
            print(f"\n{COLORS['bold']}{COLORS['green']}HypnoBot1:{COLORS['reset']} {result['final_response']}")
            
            # Show debug info if enabled
            if debug_mode:
                safety_colors = {0: "green", 1: "yellow", 2: "red"}
                safety_level = result['safety_level']
                print()
                print_colored(f"[Safety Level: {safety_level}]", safety_colors.get(safety_level, "yellow"))
                if result.get('metadata', {}).get('modifications'):
                    print_colored(f"[Modifications: {result['metadata']['modifications']}]", "blue")
                
        except Exception as e:
            print_colored(f"\nError: {str(e)}", "red")
    
if __name__ == "__main__":
    run_interactive_chat() 