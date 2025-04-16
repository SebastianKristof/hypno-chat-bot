import os
import sys
import traceback
from crewai import Crew, Process, Agent
from string import Template
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from langchain_openai import ChatOpenAI

# Add debugging output
print("Loading HypnoBot module...")
print(f"Python version: {sys.version}")
print(f"Import paths: {sys.path}")

# Add the parent directory to path if needed
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    print(f"Adding {parent_dir} to sys.path")
    sys.path.append(str(parent_dir))

try:
    # Import the agents and tasks from the config
    from config.agents import (
        categorizer, support_agent,
        safety_officer, writing_coach, accessibility_agent
    )
    from config.tasks import (
        categorization_task, initial_response_task,
        safety_check_task, writing_improvement_task,
        accessibility_task
    )
    print("✅ Successfully imported agents and tasks")
except ImportError as e:
    print(f"❌ Error importing agents and tasks: {e}")
    print(traceback.format_exc())
    # Re-try with absolute imports
    try:
        print("Trying absolute imports...")
        from src.hypnobot.config.agents import (
            categorizer, support_agent,
            safety_officer, writing_coach, accessibility_agent
        )
        from src.hypnobot.config.tasks import (
            categorization_task, initial_response_task,
            safety_check_task, writing_improvement_task,
            accessibility_task
        )
        print("✅ Successfully imported agents and tasks using absolute imports")
    except ImportError as e:
        print(f"❌ Error with absolute imports: {e}")
        print(traceback.format_exc())
        raise RuntimeError("Could not import required modules. Check your installation and paths.")

class HypnoBot:
    """
    HypnoBot v2 - A CrewAI-based hypnotherapy chatbot.
    Uses a sequential workflow of specialized agents to process user queries.
    """
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the HypnoBot with its crew of agents and tasks.
        
        Args:
            model_name: Optional model name to use (defaults to env var or gpt-3.5-turbo)
        """
        # Set up the LLM
        self.model_name = model_name or os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo")
        
        # Initialize the LLM with proper configuration for CrewAI compatibility
        try:
            print(f"Initializing LLM with model: {self.model_name}")
            self.llm = ChatOpenAI(model=self.model_name)
            
            # Assign the LLM to all agents
            for agent in [categorizer, support_agent, safety_officer, writing_coach, accessibility_agent]:
                agent.llm = self.llm
                
            # Initialize the categorization task
            self.categorization_task = categorization_task
            self.categorization_task.agent = categorizer
            
            # Initialize the full crew for appropriate queries
            print("Initializing CrewAI crew...")
            self.crew = Crew(
                agents=[
                    categorizer,
                    support_agent,
                    safety_officer,
                    writing_coach,
                    accessibility_agent
                ],
                tasks=[
                    categorization_task,
                    initial_response_task,
                    safety_check_task,
                    writing_improvement_task,
                    accessibility_task
                ],
                process=Process.sequential,
                verbose=True
            )
            print("✅ HypnoBot initialization complete")
        except AttributeError as e:
            # Catch specific compatibility issues with langchain_openai
            if "'ChatOpenAI' object has no attribute 'supports_stop_words'" in str(e):
                raise RuntimeError(
                    "Compatibility issue detected with langchain_openai. "
                    "Please ensure you have compatible versions of crewai and langchain_openai installed. "
                    "Try: pip install crewai==0.28.8 langchain-openai==0.0.2"
                ) from e
            raise
        except Exception as e:
            print(f"❌ Error during HypnoBot initialization: {e}")
            print(traceback.format_exc())
            raise
    
    def process_input(self, user_input: str) -> str:
        """
        Process a user input through the agent workflow.
        
        Args:
            user_input: The user's question or message
            
        Returns:
            The final response after processing through all agents
        """
        try:
            # Truncate input if it's too long (1500 character limit)
            MAX_CHARS = 1500
            original_length = len(user_input)
            if original_length > MAX_CHARS:
                user_input = user_input[:MAX_CHARS] + "..."
            
            # STEP 1: Categorize the inquiry
            print(f"Running categorization for input: {user_input[:30]}...")
            categorization_result = self.categorization_task.execute(inputs={"user_input": user_input})
            
            # Parse the categorization result
            is_appropriate, category, explanation = self._parse_categorization(categorization_result)
            
            # STEP 2: If inappropriate, return a polite rejection
            if not is_appropriate:
                print(f"Input categorized as inappropriate: {category}")
                return f"I'm sorry, but I can't assist with this request.\n\nCategory: {category}\nReason: {explanation}"
            
            # STEP 3: For appropriate queries, run the full workflow
            print("Input is appropriate, running full agent workflow...")
            result = self.crew.kickoff(inputs={'user_input': user_input})
            
            # Add note about truncation if input was truncated
            if original_length > MAX_CHARS:
                result += f"\n\n(Note: Your message was truncated from {original_length} to {MAX_CHARS} characters for processing.)"
            
            print("Processing complete.")
            return result
        except Exception as e:
            print(f"❌ Error processing input: {e}")
            print(traceback.format_exc())
            return f"I'm sorry, I encountered an error while processing your request: {str(e)}"
    
    def _parse_categorization(self, result: str) -> Tuple[bool, str, str]:
        """
        Parse the categorization result to determine if the query is appropriate.
        
        Args:
            result: The categorization result string
            
        Returns:
            Tuple of (is_appropriate, category, explanation)
        """
        lines = result.strip().split("\n")
        category = lines[0].upper() if lines else ""
        explanation = "\n".join(lines[1:]) if len(lines) > 1 else ""
        
        # Check if the query is appropriate for hypnotherapy discussion
        is_appropriate = "APPROPRIATE" in category
        
        return is_appropriate, category, explanation
    
    def format_task_template(self, task_description: str, inputs: Dict[str, Any]) -> str:
        """
        Format a task description template with the given inputs.
        
        Args:
            task_description: The task description with placeholders
            inputs: Dictionary of input values
            
        Returns:
            Formatted task description
        """
        # Use string formatting instead of Template.safe_substitute
        for key, value in inputs.items():
            placeholder = "{" + key + "}"
            task_description = task_description.replace(placeholder, str(value))
        
        return task_description 