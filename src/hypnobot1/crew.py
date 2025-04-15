"""
HypnoBot1Crew implementation based on the CrewAI framework.
"""

import os
import re
import sys
from typing import Dict, Any, List, Optional

from crewai import Agent, Task, Crew
from langchain_community.chat_models import ChatOpenAI

from hypnobot1.utils import get_logger, load_config, get_config_path

logger = get_logger(__name__)

class HypnoBot1Crew:
    """Hypnotherapy chatbot crew using the CrewAI framework.
    
    This implementation follows the approach from the Jupiter notebook example
    but loads configuration from YAML files.
    """
    
    def __init__(self):
        """Initialize the HypnoBot1Crew with agents and tasks from YAML config."""
        # Load configurations
        self.config_path = get_config_path()
        self.agents_config = load_config(self.config_path, "agents")
        self.tasks_config = load_config(self.config_path, "tasks")
        
        # Initialize agents
        self.agents = self._create_agents()
        
        # Log configuration status
        if not self.agents_config:
            logger.warning("Failed to load agents configuration, using empty config")
        if not self.tasks_config:
            logger.warning("Failed to load tasks configuration, using empty config")
    
    def _create_agents(self) -> Dict[str, Agent]:
        """Create CrewAI agents from YAML configuration.
        
        Returns:
            Dictionary mapping agent names to Agent instances
        """
        agents = {}
        
        # Get API key from environment variable
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        logger.info(f"API key environment variable status: {'FOUND' if openai_api_key else 'NOT FOUND'}")
        if openai_api_key:
            logger.info(f"API key length: {len(openai_api_key)}")
            logger.info(f"API key first 10 chars: {openai_api_key[:10]}...")
            
        # Check for specific patterns that might trigger OpenAI to reject the key
        if openai_api_key and ("sk-proj-" in openai_api_key or "sk-" not in openai_api_key):
            logger.warning(f"API key may be using a preview format that's not fully supported: {openai_api_key[:10]}...")
            print("Warning: Your API key starts with 'sk-proj-' which indicates a preview/project format.")
            print("This key format sometimes has compatibility issues with certain libraries.")
            
        if not openai_api_key:
            logger.error("ERROR: OPENAI_API_KEY not found in environment variables")
            print("ERROR: OPENAI_API_KEY environment variable is not set.")
            print("Please ensure your .env file contains a valid OPENAI_API_KEY and it's being loaded correctly.")
            sys.exit(1)
        
        # Verify if the API key seems valid
        if "your_" in openai_api_key or len(openai_api_key) < 20:
            logger.error(f"ERROR: OPENAI_API_KEY appears to be invalid: {openai_api_key[:10]}...")
            print("ERROR: OPENAI_API_KEY appears to be invalid or is using a placeholder value.")
            print("Please check your .env file and update with a valid API key.")
            sys.exit(1)
            
        logger.info(f"Found OpenAI API key of length {len(openai_api_key)}")
        
        # Create each agent from configuration
        for agent_name, config in self.agents_config.items():
            try:
                # Configure the LLM
                llm_config = config.get("llm", {})
                model_name = llm_config.get("model", "gpt-4")
                temperature = llm_config.get("temperature", 0.7)
                
                logger.info(f"Creating LLM with model={model_name}, temperature={temperature}")
                
                llm = ChatOpenAI(
                    model=model_name,
                    temperature=temperature,
                    api_key=openai_api_key,
                )
                
                # Create the agent
                agent = Agent(
                    role=config.get("role", f"Default {agent_name}"),
                    goal=config.get("goal", "Provide accurate information"),
                    backstory=config.get("backstory", "You are an AI assistant"),
                    verbose=config.get("verbose", True),
                    allow_delegation=config.get("allow_delegation", False),
                    llm=llm,
                )
                
                agents[agent_name] = agent
                logger.info(f"Created agent: {agent_name}")
            except Exception as e:
                logger.error(f"Error creating agent {agent_name}: {e}")
                print(f"ERROR: Failed to create agent {agent_name}: {e}")
                sys.exit(1)
        
        if not agents:
            logger.error("No agents were created. Check your configuration and API key.")
            print("ERROR: No agents were created. Check your configuration and API key.")
            sys.exit(1)
            
        return agents
    
    def _create_tasks(self, context: Dict[str, Any]) -> List[Task]:
        """Create tasks for the current interaction.
        
        Args:
            context: Context variables for the current interaction
            
        Returns:
            List of configured Task instances
        """
        tasks = []
        
        # Create hypnotherapy inquiry task
        if "hypnotherapy_inquiry" in self.tasks_config:
            inquiry_config = self.tasks_config["hypnotherapy_inquiry"]
            
            # Format the description with context variables
            description = inquiry_config.get("description", "")
            description = description.format(**context)
            
            # Add language instruction to maintain natural conversation
            language_instruction = "\nIMPORTANT: Please respond in the same language as the user's question to maintain a natural conversation."
            description += language_instruction
            
            # Get the expected output
            expected_output = inquiry_config.get("expected_output", "")
            
            # Get the agent for this task
            agent_name = inquiry_config.get("agent", "")
            agent = self.agents.get(agent_name)
            
            if agent:
                inquiry_task = Task(
                    description=description,
                    expected_output=expected_output,
                    agent=agent,
                )
                tasks.append(inquiry_task)
                logger.info("Created hypnotherapy inquiry task")
            else:
                logger.error(f"Agent {agent_name} not found for hypnotherapy inquiry task")
        
        # Create safety review task
        if "safety_review" in self.tasks_config and "hypnotherapy_response" in context:
            review_config = self.tasks_config["safety_review"]
            
            # Format the description with context variables
            description = review_config.get("description", "")
            description = description.format(**context)
            
            # Add language instruction to maintain same language
            language_instruction = "\nIMPORTANT: Please maintain the same language as the original response in your review and any modifications."
            description += language_instruction
            
            # Get the expected output
            expected_output = review_config.get("expected_output", "")
            
            # Get the agent for this task
            agent_name = review_config.get("agent", "")
            agent = self.agents.get(agent_name)
            
            if agent:
                review_task = Task(
                    description=description,
                    expected_output=expected_output,
                    agent=agent,
                )
                tasks.append(review_task)
                logger.info("Created safety review task")
            else:
                logger.error(f"Agent {agent_name} not found for safety review task")
        
        return tasks
    
    def _parse_qa_review(self, review_text) -> Dict[str, Any]:
        """Parse the QA review text to extract structured information.
        
        Args:
            review_text: The raw text response from the safety specialist or CrewOutput object
            
        Returns:
            A dictionary containing the parsed components
        """
        result = {
            "modified_response": "",
            "safety_level": 0,
            "modifications": "",
            "reasoning": ""
        }
        
        # Handle empty response
        if not review_text:
            return result
            
        try:
            # Handle different types of review_text
            logger.info(f"Review text type: {type(review_text)}")
            
            # If it's a CrewOutput object, try to extract text content
            if hasattr(review_text, 'raw_output'):
                logger.info("Converting CrewOutput to string using raw_output")
                review_text = review_text.raw_output
            elif hasattr(review_text, 'result'):
                logger.info("Converting CrewOutput to string using result")
                review_text = review_text.result
            elif hasattr(review_text, '__str__'):
                logger.info("Converting object to string using __str__")
                review_text = str(review_text)
                
            # If review_text is still not a string, try to convert it
            if not isinstance(review_text, str):
                logger.warning(f"review_text is not a string: {type(review_text)}")
                try:
                    review_text = str(review_text)
                except Exception as e:
                    logger.error(f"Failed to convert review_text to string: {e}")
                    return result
            
            # Extract the modified response
            response_match = None
            
            # Try different patterns to find the reviewed response text
            patterns = [
                r'response after review is:\s*"([^"]+)"',  # Match quoted text after "response after review is:"
                r'response is:\s*"([^"]+)"',              # Match quoted text after "response is:"
                r'response:\s*"([^"]+)"',                 # Match quoted text after "response:"
                r'The assistant\'s response.*?:\s*"([^"]+)"'  # Match quoted text after any phrase with "response"
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, review_text, re.IGNORECASE)
                if matches:
                    response_match = matches[0]
                    break
            
            # If we couldn't find with quotes, look for sections
            if not response_match:
                # Try to find a section that might contain the response
                sections = re.split(r'\n\s*(?:Safety Level Assessment|Modifications|Reasoning):', review_text)
                if sections and len(sections) > 0:
                    response_match = sections[0].strip()
            
            if response_match:
                result["modified_response"] = response_match
            
            # Extract safety level (0-4)
            safety_matches = re.findall(r'Safety Level Assessment:\s*(\d)', review_text, re.IGNORECASE)
            if not safety_matches:
                safety_matches = re.findall(r'Safety Level:\s*(\d)', review_text, re.IGNORECASE)
            
            if safety_matches:
                try:
                    result["safety_level"] = int(safety_matches[0])
                except ValueError:
                    # If not a valid integer, default to 0
                    result["safety_level"] = 0
            
            # Extract modifications
            mod_matches = re.findall(r'Modifications:(.*?)(?:\n\n|\n\s*Reasoning|\Z)', review_text, re.IGNORECASE | re.DOTALL)
            if mod_matches:
                result["modifications"] = mod_matches[0].strip()
            
            # Extract reasoning
            reason_matches = re.findall(r'Reasoning:(.*?)(?:\n\n|\Z)', review_text, re.IGNORECASE | re.DOTALL)
            if reason_matches:
                result["reasoning"] = reason_matches[0].strip()
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing QA review: {e}")
            return result
    
    def process_message(self, user_message: str, user_name: str = "User") -> Dict[str, Any]:
        """Process a user message using the CrewAI approach with proper agent collaboration.
        
        This implementation leverages CrewAI's built-in task sequencing and agent collaboration
        rather than creating separate crews and manually parsing outputs.
        
        Args:
            user_message: The user's message
            user_name: The name or identifier of the user
            
        Returns:
            A dictionary containing the processing results
        """
        try:
            # Prepare the initial context
            context = {
                "user_message": user_message,
                "user_name": user_name
            }
            
            # Create and execute the inquiry task first
            inquiry_tasks = self._create_tasks(context)
            if not inquiry_tasks:
                raise ValueError("Failed to create inquiry task")
            
            # Set up the inquiry crew
            inquiry_crew = Crew(
                agents=[agent for agent in self.agents.values()],
                tasks=[inquiry_tasks[0]],  # Just the first task (hypnotherapy inquiry)
                verbose=True,
                memory=True  # Enable crew memory
            )
            
            # Get the inquiry response
            logger.info(f"Processing inquiry from {user_name}: {user_message[:50]}...")
            inquiry_result = inquiry_crew.kickoff()
            
            # Extract the text from the inquiry result if needed
            inquiry_text = inquiry_result
            if hasattr(inquiry_result, 'raw_output'):
                logger.info("Converting inquiry CrewOutput to string using raw_output")
                inquiry_text = inquiry_result.raw_output
            elif hasattr(inquiry_result, 'result'):
                logger.info("Converting inquiry CrewOutput to string using result")
                inquiry_text = inquiry_result.result
            elif not isinstance(inquiry_result, str):
                logger.info(f"Converting inquiry result of type {type(inquiry_result)} to string")
                inquiry_text = str(inquiry_result)
                
            # Add the response to the context for the review task
            context["hypnotherapy_response"] = inquiry_text
            
            # Create and process the review task
            review_tasks = self._create_tasks(context)
            if len(review_tasks) < 2:
                logger.warning("Failed to create review task, skipping review")
                return {
                    "original_response": inquiry_text,
                    "final_response": inquiry_text,
                    "safety_level": 0,
                    "metadata": {
                        "review_skipped": True
                    }
                }
            
            # Set up the review crew
            review_crew = Crew(
                agents=[agent for agent in self.agents.values()],
                tasks=[review_tasks[1]],  # The second task (safety review)
                verbose=True,
                memory=True  # Enable crew memory
            )
            
            # Get the review result
            logger.info("Processing safety review...")
            review_result = review_crew.kickoff()
            
            # Parse the review result
            parsed_review = self._parse_qa_review(review_result)
            
            # Determine the final response
            final_response = parsed_review["modified_response"]
            if not final_response.strip():
                logger.info("Using original response as final response (no modified response found)")
                final_response = inquiry_text
            
            # Return the structured result
            return {
                "original_response": inquiry_text,
                "final_response": final_response,
                "safety_level": parsed_review["safety_level"],
                "metadata": {
                    "review_result": str(review_result),
                    "modifications": parsed_review["modifications"],
                    "reasoning": parsed_review["reasoning"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "original_response": "",
                "final_response": "I apologize, but I encountered an issue processing your message. Please try again.",
                "safety_level": 2,  # Cautious middle ground
                "metadata": {"error": str(e)}
            } 