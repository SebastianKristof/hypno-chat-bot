import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the system path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

# Optional memory patch if needed
try:
    from src.hypnobot.memory_patch import patch_memory
    patch_memory()
    print("✅ Applied memory patch to avoid embedchain dependency issues")
except ImportError:
    pass  # No memory patch module present = not an issue
except Exception as e:
    print(f"⚠️ Warning: Memory patch failed: {e}")

# Import HypnoBot
from src.hypnobot.v2.hypnobot import HypnoBot

def main():
    print("🧠 HypnoBot v2 - Hypnotherapy Chatbot")
    print("Type 'exit' to quit the chat")
    print("-" * 50)

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables.")
        print("Please create a .env file (you can use .env.example)")
        return

    try:
        print("⚙️ Initializing HypnoBot...")
        bot = HypnoBot()
        print("✅ Ready to chat!")

        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ("exit", "quit", "bye"):
                print("HypnoBot: Goodbye! Take care.")
                break

            try:
                print("🤖 Thinking...")
                response = bot.process_input(user_input)
                print(f"\nHypnoBot: {response}")
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("HypnoBot: I'm sorry, something went wrong.")

    except Exception as e:
        print(f"❌ Error initializing HypnoBot: {e}")
        print("Please check your dependencies and configuration.")

if __name__ == "__main__":
    main()
