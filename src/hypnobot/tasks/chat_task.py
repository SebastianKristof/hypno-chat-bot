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
        self.using_default_config = False
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load the task configuration from YAML."""
        try:
            with open(self.config_path, "r") as file:
                config = yaml.safe_load(file)
                task_config = config.get("chat_task", {})
                if not task_config:
                    logger.warning("Chat task configuration is empty or missing in YAML")
                    self.using_default_config = True
                return task_config
        except Exception as e:
            logger.error(f"Error loading chat task config: {e}")
            self.using_default_config = True
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
        
        # Get context if available
        context = self.config.get("context", [])
        
        # Log warning if using default configuration
        if self.using_default_config:
            logger.warning("Using default chat task configuration")
        
        # Create and return the task
        return Task(
            description=description,
            expected_output=expected_output,
            context=context,
            async_execution=False,
            human_input=None,
            output_file=None
        )
        
    def is_using_default_config(self) -> bool:
        """Check if the task is using default configuration.
        
        Returns:
            True if using default configuration, False if using loaded configuration.
        """
        return self.using_default_config 