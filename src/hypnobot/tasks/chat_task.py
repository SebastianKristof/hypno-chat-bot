import os
from typing import Dict, Any, Optional

from crewai import Task
import yaml

from hypnobot.utils.logging import get_logger

logger = get_logger(__name__)

class ChatTask:
    """Chat task for the hypnotherapy chatbot.
    
    This task is responsible for processing user messages and
    generating appropriate responses using the client-facing agent.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the chat task.
        
        Args:
            config_path: Path to the task configuration file.
                If None, uses the default config path.
        """
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "..", "config", "tasks.yaml"
        )
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load the task configuration from YAML."""
        try:
            with open(self.config_path, "r") as file:
                config = yaml.safe_load(file)
                return config.get("chat_task", {})
        except Exception as e:
            logger.error(f"Error loading chat task config: {e}")
            # Return a default configuration if loading fails
            return {
                "description": "Respond to the user's message in a calm, empathetic, and informative tone.",
                "expected_output": "A calming, clear response that addresses the user's question.",
                "agent": "client_agent",
                "context": [],
            }
    
    def create_task(self, user_input: str, agent_name: Optional[str] = None) -> Task:
        """Create a CrewAI task for the chat interaction.
        
        Args:
            user_input: The user's message text.
            agent_name: Name of the agent to assign the task to.
                If None, uses the agent specified in the config.
                
        Returns:
            A configured CrewAI Task instance.
        """
        # Get task description and format with user input
        description = self.config.get(
            "description", 
            "Respond to the user's message in a calm, empathetic, and informative tone."
        )
        description = description.format(user_input=user_input)
        
        # Get expected output format
        expected_output = self.config.get(
            "expected_output",
            "A calming, clear response that addresses the user's question."
        )
        
        # Get agent name from config if not provided
        if agent_name is None:
            agent_name = self.config.get("agent", "client_agent")
        
        # Get context if available
        context = self.config.get("context", [])
        
        # Create and return the task
        return Task(
            description=description,
            expected_output=expected_output,
            agent=agent_name,  # This will be replaced with the actual agent instance by CrewAI
            context=context,
        ) 