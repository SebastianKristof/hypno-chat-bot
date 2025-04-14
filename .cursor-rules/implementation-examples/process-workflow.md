# Process Workflow Implementation Example

This document provides a sample implementation of the CrewAI Process class for the hypnotherapy chatbot workflow.

## Crew and Process Setup (crew/processes.py)

```python
"""
Process workflow definitions for the hypnotherapy chatbot.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from crewai import Process, Task, Agent

class HypnoChatProcess:
    """
    Defines the process workflow for handling user queries in the hypnotherapy chatbot.
    """
    
    def __init__(
        self,
        client_agent: Agent,
        qa_agent: Agent,
        chat_task: Task,
        review_task: Task
    ):
        """
        Initialize the process workflow with required agents and tasks.
        
        Args:
            client_agent: The client-facing agent for generating initial responses
            qa_agent: The QA/safety agent for reviewing content
            chat_task: The task for generating user responses
            review_task: The task for reviewing responses for safety
        """
        self.client_agent = client_agent
        self.qa_agent = qa_agent
        self.chat_task = chat_task
        self.review_task = review_task
        
    def create_process(self) -> Process:
        """
        Create and return a configured Process instance.
        
        Returns:
            A CrewAI Process instance configured for the hypnotherapy chat workflow
        """
        return Process(
            name="HypnotherapyChatProcess",
            description="Process user queries with safety monitoring for a hypnotherapy chatbot",
            tasks=[self.chat_task, self.review_task],
            agents=[self.client_agent, self.qa_agent],
            flow={
                self.chat_task: [self.review_task],  # Review task follows chat task
                self.review_task: []                 # End of process
            },
            verbose=True
        )
    
    async def execute_process(self, user_query: str) -> Dict[str, Any]:
        """
        Execute the chat process for a given user query.
        
        Args:
            user_query: The user's input message
            
        Returns:
            A dictionary containing the process results
        """
        # Create the process
        process = self.create_process()
        
        # Initialize process inputs
        process_inputs = {
            "user_query": user_query,
            "timestamp": datetime.now().isoformat()
        }
        
        # Create a persistent state dictionary to pass between tasks
        state = {
            "conversation_history": [],  # To store conversation history
            "safety_interventions": []   # To track safety interventions
        }
        
        # Execute the process
        try:
            result = await process.execute(
                inputs=process_inputs,
                state=state
            )
            
            # Format the final response
            final_response = {
                "user_query": user_query,
                "client_response": result.get(self.chat_task.name, {}).get("response", ""),
                "safety_analysis": result.get(self.review_task.name, {}).get("safety_analysis", {}),
                "final_response": result.get(self.review_task.name, {}).get("final_response", ""),
                "timestamp": datetime.now().isoformat(),
                "state": state
            }
            
            return final_response
            
        except Exception as e:
            # Handle process execution errors
            error_response = {
                "error": str(e),
                "status": "failed",
                "user_query": user_query,
                "fallback_response": "I apologize, but I'm having trouble processing your request. Please try again in a moment."
            }
            return error_response
```

## How Tasks Connect to this Process (tasks/chat_task.py)

```python
"""
Chat task implementation for the hypnotherapy chatbot.
"""
from crewai import Task
from typing import Dict, Any, List, Optional

def create_chat_task() -> Task:
    """
    Create the chat task for generating responses to user queries.
    
    Returns:
        A configured Task instance
    """
    return Task(
        name="generate_response",
        description="""
        Generate a supportive, informative response to the user's query about hypnotherapy.
        Focus on being educational while maintaining appropriate boundaries.
        
        User query: {user_query}
        """,
        expected_output="""
        {
            "response": "The generated response to the user",
            "confidence": 0.95,
            "topics": ["identified", "topics", "from", "query"],
            "requires_safety_review": true
        }
        """,
        async_execution=True,
        context=[],  # Optional additional context
    )

async def execute_chat_task(
    agent, 
    task: Task, 
    inputs: Dict[str, Any], 
    state: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Custom execution function for the chat task.
    
    Args:
        agent: The agent executing the task
        task: The task being executed
        inputs: The task inputs
        state: The process state
        
    Returns:
        The task output
    """
    # Extract user query from inputs
    user_query = inputs.get("user_query", "")
    
    # Update state with the current query
    if "conversation_history" in state:
        state["conversation_history"].append({
            "role": "user",
            "content": user_query,
            "timestamp": inputs.get("timestamp")
        })
    
    # Execute the task using the agent
    task_output = await agent.execute_task(
        task=task,
        inputs=inputs
    )
    
    # Update the state with the agent's response
    if "conversation_history" in state:
        state["conversation_history"].append({
            "role": "assistant",
            "content": task_output.get("response", ""),
            "timestamp": inputs.get("timestamp")
        })
    
    return task_output
```

## How Tasks Connect to this Process (tasks/review_task.py)

```python
"""
Review task implementation for the hypnotherapy chatbot.
"""
from crewai import Task
from typing import Dict, Any, List, Optional

def create_review_task() -> Task:
    """
    Create the review task for evaluating response safety.
    
    Returns:
        A configured Task instance
    """
    return Task(
        name="review_response",
        description="""
        Review the proposed response for safety concerns, scope violations, and ethical issues.
        
        User query: {user_query}
        Proposed response: {client_response}
        """,
        expected_output="""
        {
            "safety_analysis": {
                "safety_level": 0-4,
                "triggers": ["trigger1", "trigger2"],
                "intervention_type": "none|adjust|redirect|block|escalate",
                "reasoning": "Explanation of analysis and decision"
            },
            "final_response": "The approved or modified response to be sent to the user"
        }
        """,
        async_execution=True,
        context=[],  # Optional additional context
    )

async def execute_review_task(
    agent, 
    task: Task, 
    inputs: Dict[str, Any], 
    previous_outputs: Dict[str, Any],
    state: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Custom execution function for the review task.
    
    Args:
        agent: The agent executing the task
        task: The task being executed
        inputs: The task inputs
        previous_outputs: Outputs from previous tasks
        state: The process state
        
    Returns:
        The task output
    """
    # Extract user query from inputs
    user_query = inputs.get("user_query", "")
    
    # Extract client response from previous task output
    client_task_output = previous_outputs.get("generate_response", {})
    client_response = client_task_output.get("response", "")
    
    # Create task inputs for the review
    review_inputs = {
        "user_query": user_query,
        "client_response": client_response
    }
    
    # Execute the review task
    task_output = await agent.execute_task(
        task=task,
        inputs=review_inputs
    )
    
    # Track safety interventions if needed
    safety_analysis = task_output.get("safety_analysis", {})
    intervention_type = safety_analysis.get("intervention_type", "none")
    
    if intervention_type != "none" and "safety_interventions" in state:
        state["safety_interventions"].append({
            "user_query": user_query,
            "client_response": client_response,
            "safety_analysis": safety_analysis,
            "final_response": task_output.get("final_response", ""),
            "timestamp": inputs.get("timestamp")
        })
    
    # Update conversation history with final response
    if "conversation_history" in state:
        # Remove the preliminary assistant response
        if len(state["conversation_history"]) > 0 and state["conversation_history"][-1]["role"] == "assistant":
            state["conversation_history"].pop()
        
        # Add the final response
        state["conversation_history"].append({
            "role": "assistant",
            "content": task_output.get("final_response", ""),
            "timestamp": inputs.get("timestamp")
        })
    
    return task_output
```

## How to Use the Process (api/routes/chat.py)

```python
"""
Chat route implementation for the hypnotherapy chatbot API.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

from hypnobot.crew.processes import HypnoChatProcess

router = APIRouter()

class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    conversation_id: str
    safety_level: int = 0
    intervention_type: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    hypno_process: HypnoChatProcess = Depends()
) -> ChatResponse:
    """
    Process a chat message and return a response.
    
    Args:
        request: The chat request
        hypno_process: The hypnotherapy chat process
        
    Returns:
        A chat response
    """
    try:
        # Execute the process with the user's message
        process_result = await hypno_process.execute_process(
            user_query=request.message
        )
        
        # Extract the required information
        final_response = process_result.get("final_response", "")
        safety_analysis = process_result.get("safety_analysis", {})
        safety_level = safety_analysis.get("safety_level", 0)
        intervention_type = safety_analysis.get("intervention_type", "none")
        
        # Generate or retrieve conversation ID
        conversation_id = request.conversation_id or f"conv_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return ChatResponse(
            response=final_response,
            conversation_id=conversation_id,
            safety_level=safety_level,
            intervention_type=intervention_type
        )
        
    except Exception as e:
        # Handle errors
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )
```

## CrewAI Process Benefits for Hypnotherapy Chatbot

Using CrewAI's Process class for this workflow provides several advantages:

1. **Explicit Task Sequencing**: The process clearly defines that the review task must follow the chat task, ensuring proper safety checks.

2. **State Management**: The state dictionary persists across task executions, allowing tracking of conversation history and safety interventions.

3. **Error Handling**: Centralized error handling in the process execution makes the system more robust.

4. **Flexibility**: The workflow can be easily extended to include additional tasks, such as pre-processing user queries or post-processing responses.

5. **Monitoring**: The verbose mode allows tracking the execution flow for debugging and monitoring.

6. **Asynchronous Execution**: All tasks support async execution for better performance and responsiveness.

By implementing this pattern, the hypnotherapy chatbot maintains a clear separation between generating responses and ensuring their safety, while providing a cohesive workflow for processing user queries. 