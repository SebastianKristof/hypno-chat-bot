import os
import sys
from crewai import Crew, Process, Agent
from string import Template
from pathlib import Path
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI

# Import the agents and tasks from the config
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.agents import (
    categorizer, support_agent,
    safety_officer, writing_coach, accessibility_agent
)
from config.tasks import (
    categorization_task, initial_response_task,
    safety_check_task, writing_improvement_task,
    accessibility_task
)

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
        self.llm = ChatOpenAI(model=self.model_name)
        
        # Assign the LLM to all agents
        for agent in [categorizer, support_agent, safety_officer, writing_coach, accessibility_agent]:
            agent.llm = self.llm
        
        # Initialize the crew
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
    
    def process_input(self, user_input: str) -> str:
        """
        Process a user input through the agent workflow.
        
        Args:
            user_input: The user's question or message
            
        Returns:
            The final response after processing through all agents
        """
        # Process the input through the crew
        result = self.crew.kickoff(inputs={'user_input': user_input})
        
        # Return the final output
        return result
    
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