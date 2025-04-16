"""
HypnoBot1Crew implementation based on the CrewAI framework.
"""

import os
import re
import sys
from typing import Dict, Any, List, Optional

from crewai import Agent, Task, Crew
from langchain_community.chat_models import ChatOpenAI

from hypnobot1.utils import get_logger, load_config, get_config_path, calculate_cost

logger = get_logger(__name__)

logger.info("Using direct token tracking through CrewAI's built-in mechanisms")


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
    
    def _manually_track_token_usage(self, crew_obj) -> Dict[str, int]:
        """Manually calculate token usage by checking crew's callback_manager.
        
        Args:
            crew_obj: The CrewAI crew object
            
        Returns:
            Dictionary with token usage metrics
        """
        token_usage = {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "successful_requests": 0
        }
        
        try:
            # First try the calculate_usage_metrics method
            if hasattr(crew_obj, 'calculate_usage_metrics'):
                try:
                    crew_obj.calculate_usage_metrics()
                    logger.info("Called calculate_usage_metrics()")
                except Exception as e:
                    logger.warning(f"Error calculating usage metrics: {e}")
            
            # Try to access the usage_metrics attribute
            if hasattr(crew_obj, 'usage_metrics'):
                try:
                    metrics = crew_obj.usage_metrics
                    logger.info(f"Got usage_metrics: {metrics}")
                    
                    # Try to extract values from metrics object
                    token_usage["total_tokens"] = getattr(metrics, "total_tokens", 0)
                    token_usage["prompt_tokens"] = getattr(metrics, "prompt_tokens", 0)
                    token_usage["completion_tokens"] = getattr(metrics, "completion_tokens", 0)
                    token_usage["successful_requests"] = getattr(metrics, "successful_requests", 0)
                    
                    # If we got at least one non-zero value, we're good
                    if token_usage["total_tokens"] > 0 or token_usage["prompt_tokens"] > 0:
                        logger.info(f"Successfully extracted token usage: {token_usage}")
                        return token_usage
                except Exception as e:
                    logger.warning(f"Error accessing usage_metrics: {e}")
            
            # If we're here, we need to estimate token usage
            logger.warning("Unable to get accurate token usage, using estimate")
            
            # Rough estimate based on typical token ratios
            if hasattr(crew_obj, 'callbacks'):
                cb_count = len(getattr(crew_obj, 'callbacks', []))
                logger.info(f"Crew has {cb_count} callbacks")
        
            # Estimate based on typical patterns
            # Each task typically uses at least several thousand tokens
            num_tasks = len(getattr(crew_obj, 'tasks', []))
            num_agents = len(getattr(crew_obj, 'agents', []))
            
            logger.info(f"Crew has {num_tasks} tasks and {num_agents} agents")
            
            # Very rough estimate assuming ~3000 prompt tokens and ~1000 completion tokens per task
            token_usage["prompt_tokens"] = num_tasks * 3000
            token_usage["completion_tokens"] = num_tasks * 1000
            token_usage["total_tokens"] = token_usage["prompt_tokens"] + token_usage["completion_tokens"]
            token_usage["successful_requests"] = num_tasks
            
            logger.info(f"Estimated token usage: {token_usage}")
            
        except Exception as e:
            logger.error(f"Error tracking token usage: {e}")
        
        return token_usage
        
    def process_message(self, user_message: str, user_name: str = "User") -> Dict[str, Any]:
        """Process a user message using the CrewAI approach with proper agent collaboration.
        
        This implementation leverages CrewAI's built-in task sequencing and agent collaboration
        using a single crew with multiple agents and tasks.
        
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
            
            # Create all tasks
            inquiry_tasks = self._create_tasks(context)
            if not inquiry_tasks:
                raise ValueError("Failed to create inquiry task")
            
            # Get the inquiry task first
            inquiry_task = inquiry_tasks[0]
            
            # Create the hypnotherapy response first
            logger.info(f"Processing inquiry from {user_name}: {user_message[:50]}...")
            
            # Set up the inquiry crew with just one task to get the initial response
            inquiry_crew = Crew(
                agents=[agent for agent in self.agents.values()],
                tasks=[inquiry_task],
                verbose=True,
                memory=True
            )
            
            # Get the inquiry response
            inquiry_result = inquiry_crew.kickoff()
            
            # Track token usage for inquiry
            inquiry_token_usage = self._manually_track_token_usage(inquiry_crew)
            logger.info(f"Inquiry token usage: {inquiry_token_usage}")
            
            # Extract the inquiry response text
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
                
            # Update the context with the hypnotherapy response
            context["hypnotherapy_response"] = inquiry_text
            
            # Create all tasks including the review task with updated context
            all_tasks = self._create_tasks(context)
            if len(all_tasks) < 2:
                logger.warning("Failed to create review task, returning inquiry result only")
                
                # Calculate cost for inquiry
                inquiry_model = self.agents_config.get("hypnotherapy_guide", {}).get("llm", {}).get("model", "gpt-4o-mini")
                inquiry_cost = calculate_cost(inquiry_token_usage, inquiry_model)
                
                return {
                    "original_response": inquiry_text,
                    "final_response": inquiry_text,
                    "safety_level": 0,
                    "token_usage": inquiry_token_usage,
                    "cost_info": inquiry_cost,
                    "metadata": {
                        "review_skipped": True
                    }
                }
            
            # Now set up a single crew with both agents and both tasks
            crew = Crew(
                agents=[agent for agent in self.agents.values()],
                tasks=all_tasks,  # Include both inquiry and review tasks
                verbose=True,
                memory=True
            )
            
            # Run the full crew process with both tasks
            logger.info("Processing with full crew (inquiry + review)...")
            result = crew.kickoff()
            
            # Track token usage for full crew
            token_usage = self._manually_track_token_usage(crew)
            logger.info(f"Full crew token usage: {token_usage}")
            
            # Calculate costs based on both agents' models
            inquiry_model = self.agents_config.get("hypnotherapy_guide", {}).get("llm", {}).get("model", "gpt-4o-mini")
            review_model = self.agents_config.get("safety_specialist", {}).get("llm", {}).get("model", "gpt-4o-mini")
            
            # Calculate cost info
            cost_info = calculate_cost(token_usage, inquiry_model)
            cost_info['models'] = {
                'inquiry': inquiry_model,
                'review': review_model
            }
            
            # Parse the review result from the crew output
            parsed_review = self._parse_qa_review(result)
            
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
                "token_usage": token_usage,
                "cost_info": cost_info,
                "metadata": {
                    "review_result": str(result),
                    "modifications": parsed_review["modifications"],
                    "reasoning": parsed_review["reasoning"],
                    "inquiry_token_usage": inquiry_token_usage
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "original_response": "",
                "final_response": "I apologize, but I encountered an issue processing your message. Please try again.",
                "safety_level": 2,  # Cautious middle ground
                "token_usage": {"total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0, "successful_requests": 0},
                "cost_info": {"total_cost": 0, "input_cost": 0, "output_cost": 0, "models": {}, "tokens": {"prompt": 0, "completion": 0, "total": 0}},
                "metadata": {"error": str(e)}
            } 