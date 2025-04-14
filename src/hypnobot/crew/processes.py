from typing import Dict, Any, List, Optional, Union

from crewai import Crew, Agent, Task
from crewai.process import Process

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
    
    def _extract_text_from_crew_output(self, crew_output: Any) -> str:
        """Extract text from a CrewOutput object or other result type.
        
        Args:
            crew_output: Output from crew.kickoff(), which could be
                a CrewOutput object, string, or other type.
                
        Returns:
            The extracted text as a string.
        """
        # Handle CrewOutput object from newer crewai versions
        if hasattr(crew_output, "raw_output"):
            return str(crew_output.raw_output)
        elif hasattr(crew_output, "output"):
            return str(crew_output.output)
        # For crewai >=0.23.0, results attribute might contain task outputs
        elif hasattr(crew_output, "results") and hasattr(crew_output.results, "values"):
            # Try to get the first result
            values = list(crew_output.results.values())
            if values:
                return str(values[0])
        # Handle simple string output
        elif isinstance(crew_output, str):
            return crew_output
        # Last resort: convert to string
        return str(crew_output)
    
    def create_process(self, user_message: str) -> Crew:
        """Create a CrewAI crew for handling a user message.
        
        Args:
            user_message: The user's message text.
            
        Returns:
            A configured CrewAI Crew instance.
        """
        # Create the chat task
        chat_task = self.chat_task_creator.create_task(user_message)
        chat_task.agent = self.client_agent
        
        # In the newer crewai versions, direct task dependencies work differently
        # We need to use a callback approach for the task chain
        
        # Create the crew with just the chat task initially
        crew = Crew(
            agents=[self.client_agent, self.qa_agent],
            tasks=[chat_task],
            verbose=True
        )
        
        return crew
    
    def process_message(self, user_message: str) -> Dict[str, Any]:
        """Process a user message using the defined process.
        
        Args:
            user_message: The user's message text.
            
        Returns:
            A dictionary containing the processing results.
        """
        try:
            # Create and run the crew for the chat task
            crew = self.create_process(user_message)
            crew_output = crew.kickoff()
            
            # Extract the actual text result from the CrewOutput object
            chat_result = self._extract_text_from_crew_output(crew_output)
            logger.info(f"Chat result: {chat_result}")
            
            # Safety check - only proceed with QA if we have a valid chat result
            if not chat_result or (isinstance(chat_result, str) and len(chat_result.strip()) == 0):
                return {
                    "original_response": "",
                    "final_response": "I apologize, but I couldn't generate a response. Please try again.",
                    "safety_level": 2,  # Cautious middle ground
                    "metadata": {"error": "Empty chat result"},
                }
            
            # Now run a separate QA check on the chat result
            try:
                # Create a QA review task with the chat result
                review_task = self.review_task_creator.create_task(chat_result)
                review_task.agent = self.qa_agent
                
                # Create a separate crew just for the review
                review_crew = Crew(
                    agents=[self.qa_agent],
                    tasks=[review_task],
                    verbose=True
                )
                
                # Run the review
                review_output = review_crew.kickoff()
                review_result = self._extract_text_from_crew_output(review_output)
                logger.info(f"Review result: {review_result}")
                
                # Determine safety level from review result
                safety_level = 0  # Default - safe
                if isinstance(review_result, str):
                    if "unsafe" in review_result.lower():
                        safety_level = 2  # Unsafe
                    elif "caution" in review_result.lower():
                        safety_level = 1  # Caution
                
                # Use the original chat result as the response
                return {
                    "original_response": chat_result,
                    "final_response": chat_result,  # Could be modified based on review in future
                    "safety_level": safety_level,
                    "metadata": {"review_result": review_result},
                }
                
            except Exception as review_error:
                logger.error(f"Error during review: {str(review_error)}")
                # If review fails, we still return the chat result but mark it with caution
                return {
                    "original_response": chat_result,
                    "final_response": chat_result,
                    "safety_level": 1,  # Caution since review failed
                    "metadata": {"error": f"Review error: {str(review_error)}"},
                }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "original_response": "",
                "final_response": "I apologize, but I encountered an issue processing your message. Please try again.",
                "safety_level": 2,  # Cautious middle ground
                "metadata": {"error": str(e)},
            } 