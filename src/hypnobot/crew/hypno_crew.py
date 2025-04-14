from typing import Dict, Any, List, Optional

from crewai import Crew, Agent, Task

from hypnobot.agents import ClientAgent, QAAgent
from hypnobot.tasks import ChatTask, ReviewTask
from hypnobot.utils.logging import get_logger

logger = get_logger(__name__)

class HypnoCrew:
    """Hypnotherapy chatbot crew.
    
    This class coordinates the agents and tasks for the hypnotherapy chatbot,
    creating a workflow for processing user messages and generating safe,
    informative responses.
    """
    
    def __init__(self):
        """Initialize the hypnotherapy chatbot crew."""
        # Initialize agents
        self.client_agent_wrapper = ClientAgent()
        self.qa_agent_wrapper = QAAgent()
        
        # Get agent instances
        self.client_agent = self.client_agent_wrapper.get_agent()
        self.qa_agent = self.qa_agent_wrapper.get_agent()
        
        # Initialize task creators
        self.chat_task_creator = ChatTask()
        self.review_task_creator = ReviewTask()
        
        # Initialize the crew
        self.crew = self._create_crew()
    
    def _create_crew(self) -> Crew:
        """Create the CrewAI crew with the configured agents.
        
        Returns:
            A configured CrewAI Crew instance.
        """
        return Crew(
            agents=[self.client_agent, self.qa_agent],
            tasks=[],  # Tasks will be added dynamically for each interaction
            verbose=True,
        )
    
    def process_message(self, user_message: str) -> Dict[str, Any]:
        """Process a user message and generate a response.
        
        Args:
            user_message: The user's message text.
            
        Returns:
            A dictionary containing:
                - original_response: The initial response from the client agent
                - final_response: The reviewed and possibly modified response
                - safety_level: The safety level assessment (0-4)
                - metadata: Additional information about the processing
        """
        logger.info(f"Processing user message: {user_message[:50]}...")
        
        try:
            # Create tasks for this specific interaction
            chat_task = self.chat_task_creator.create_task(user_message)
            
            # Assign the actual agent instance to the task
            chat_task.agent = self.client_agent
            
            # Execute the chat task to get the initial response
            self.crew.tasks = [chat_task]  # Replace any existing tasks
            chat_result = self.crew.kickoff()
            
            logger.info("Chat task completed, starting review task...")
            
            # Create and execute the review task
            review_task = self.review_task_creator.create_task(chat_result)
            review_task.agent = self.qa_agent
            
            self.crew.tasks = [review_task]  # Replace the chat task
            review_result = self.crew.kickoff()
            
            # Parse the review result
            # Expecting something like: {"final_response": "...", "safety_level": 0}
            if isinstance(review_result, dict):
                # The QA agent returned a structured response
                final_response = review_result.get("final_response", review_result)
                safety_level = review_result.get("safety_level", 0)
                metadata = {k: v for k, v in review_result.items() 
                           if k not in ["final_response", "safety_level"]}
            else:
                # The QA agent returned just the text response
                final_response = review_result
                safety_level = 0
                metadata = {}
            
            return {
                "original_response": chat_result,
                "final_response": final_response,
                "safety_level": safety_level,
                "metadata": metadata,
            }
        
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "original_response": "",
                "final_response": "I apologize, but I encountered an issue processing your message. Please try again.",
                "safety_level": 2,  # Cautious middle ground
                "metadata": {"error": str(e)},
            } 