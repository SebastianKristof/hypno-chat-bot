from typing import Dict, Any, List, Optional

from crewai import Process, Agent, Task

from hypnobot.agents import ClientAgent, QAAgent
from hypnobot.tasks import ChatTask, ReviewTask
from hypnobot.utils.logging import get_logger

logger = get_logger(__name__)

class HypnoChatProcess:
    """Hypnotherapy chatbot process.
    
    This class defines the workflow process for the hypnotherapy chatbot,
    creating a structured pipeline for handling user messages through
    multiple agent interactions.
    """
    
    def __init__(self):
        """Initialize the hypnotherapy chatbot process."""
        # Initialize agents
        self.client_agent_wrapper = ClientAgent()
        self.qa_agent_wrapper = QAAgent()
        
        # Get agent instances
        self.client_agent = self.client_agent_wrapper.get_agent()
        self.qa_agent = self.qa_agent_wrapper.get_agent()
        
        # Initialize task creators
        self.chat_task_creator = ChatTask()
        self.review_task_creator = ReviewTask()
    
    def create_process(self, user_message: str) -> Process:
        """Create a CrewAI process for handling a user message.
        
        Args:
            user_message: The user's message text.
            
        Returns:
            A configured CrewAI Process instance.
        """
        # Create the chat task
        chat_task = self.chat_task_creator.create_task(user_message)
        chat_task.agent = self.client_agent
        
        # Define a placeholder for the review task that will be created after chat task completes
        # We'll use the output of the chat task as input to this task
        def create_review_task(chat_result: str) -> Task:
            review_task = self.review_task_creator.create_task(chat_result)
            review_task.agent = self.qa_agent
            return review_task
        
        # Define the process
        process = Process(
            name="HypnotherapyChatProcess",
            description="Process user queries with safety monitoring",
            tasks=[chat_task],  # Start with just the chat task
            agents=[self.client_agent, self.qa_agent],
        )
        
        # Define task callbacks
        @process.on_task_complete(chat_task)
        def on_chat_complete(result: str) -> Dict[str, Any]:
            """Callback for when chat task completes."""
            logger.info("Chat task completed, creating review task...")
            
            # Create and add the review task with the chat result
            review_task = create_review_task(result)
            process.add_task(review_task)
            
            # Store the chat result for later reference
            return {"chat_result": result}
        
        return process
    
    def process_message(self, user_message: str) -> Dict[str, Any]:
        """Process a user message using the defined process.
        
        Args:
            user_message: The user's message text.
            
        Returns:
            A dictionary containing the processing results.
        """
        try:
            # Create and run the process
            process = self.create_process(user_message)
            result = process.execute()
            
            # Extract and return the final result
            return {
                "original_response": result.get("chat_result", ""),
                "final_response": result.get("final_result", result),
                "safety_level": result.get("safety_level", 0),
                "metadata": {k: v for k, v in result.items() 
                           if k not in ["chat_result", "final_result", "safety_level"]},
            }
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "original_response": "",
                "final_response": "I apologize, but I encountered an issue processing your message. Please try again.",
                "safety_level": 2,  # Cautious middle ground
                "metadata": {"error": str(e)},
            } 