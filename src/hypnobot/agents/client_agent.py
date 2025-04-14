import os
from typing import Dict, Any, Optional

from crewai import Agent
from langchain_community.chat_models import ChatOpenAI
import yaml

from hypnobot.utils.logging import get_logger

logger = get_logger(__name__)

class ClientAgent:
    """Client-facing agent for the hypnotherapy chatbot.
    
    This agent is responsible for interacting with the user,
    providing information about hypnotherapy, and maintaining
    a supportive, informative tone.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the client agent.
        
        Args:
            config_path: Path to the agent configuration file.
                If None, uses the default config path.
        """
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "..", "config", "agents.yaml"
        )
        self.using_default_config = False
        self.config = self._load_config()
        self.agent = self._create_agent()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load the agent configuration from YAML."""
        try:
            with open(self.config_path, "r") as file:
                config = yaml.safe_load(file)
                agent_config = config.get("client_agent", {})
                if not agent_config:
                    logger.warning("Client agent configuration is empty or missing in YAML")
                    self.using_default_config = True
                return agent_config
        except Exception as e:
            logger.error(f"Error loading client agent config: {e}")
            self.using_default_config = True
            # Return a default configuration if loading fails
            return {
                "role": "Hypnotherapy Guide",
                "goal": "Provide accurate information about hypnotherapy",
                "backstory": "You are an experienced hypnotherapy guide.",
                "verbose": True,
                "llm": {"model": "gpt-4", "temperature": 0.7},
            }
    
    def _create_agent(self) -> Agent:
        """Create the CrewAI agent with the loaded configuration."""
        # Get API key from environment variable
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not openai_api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
        
        # Configure the LLM
        llm_config = self.config.get("llm", {})
        llm = ChatOpenAI(
            model=llm_config.get("model", "gpt-4"),
            temperature=llm_config.get("temperature", 0.7),
            api_key=openai_api_key,
        )
        
        # Create the agent
        agent = Agent(
            role=self.config.get("role", "Hypnotherapy Guide"),
            goal=self.config.get("goal", "Provide accurate information about hypnotherapy"),
            backstory=self.config.get("backstory", "You are an experienced hypnotherapy guide."),
            verbose=self.config.get("verbose", True),
            allow_delegation=self.config.get("allow_delegation", False),
            llm=llm,
        )
        
        # Log warning if using default configuration
        if self.using_default_config:
            logger.warning("Using default client agent configuration")
        
        return agent
    
    def get_agent(self) -> Agent:
        """Get the configured CrewAI agent instance."""
        return self.agent
        
    def is_using_default_config(self) -> bool:
        """Check if the agent is using default configuration.
        
        Returns:
            True if using default configuration, False if using loaded configuration.
        """
        return self.using_default_config 