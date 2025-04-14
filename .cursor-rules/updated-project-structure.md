# Updated Project Structure: Hypnotherapy Chatbot

This document outlines the recommended project structure for the hypnotherapy chatbot application following CrewAI best practices.

## Directory Structure

```
hypnobot/
├── README.md                     # Project overview and setup instructions
├── pyproject.toml                # Project metadata and dependencies (Poetry)
├── requirements.txt              # Dependencies (alternative to Poetry)
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore patterns
│
├── src/                          # Source code
│   ├── hypnobot/                 # Main package
│   │   ├── __init__.py           # Package initialization
│   │   │
│   │   ├── agents/               # Agent definitions
│   │   │   ├── __init__.py       # Agent exports
│   │   │   ├── client_agent.py   # Client-facing agent implementation
│   │   │   └── qa_agent.py       # QA/Safety agent implementation
│   │   │
│   │   ├── tasks/                # Task definitions
│   │   │   ├── __init__.py       # Task exports
│   │   │   ├── chat_task.py      # User interaction task
│   │   │   └── review_task.py    # Content review task
│   │   │
│   │   ├── tools/                # Custom tools
│   │   │   ├── __init__.py       # Tool exports
│   │   │   ├── knowledge_tool.py # Knowledge retrieval tool
│   │   │   └── safety_tool.py    # Content safety evaluation tool
│   │   │
│   │   ├── crew/                 # Crew and process configuration
│   │   │   ├── __init__.py       # Crew exports
│   │   │   ├── hypno_crew.py     # Main crew definition
│   │   │   └── processes.py      # Process workflows
│   │   │
│   │   ├── config/               # Configuration
│   │   │   ├── __init__.py       # Config exports
│   │   │   ├── settings.py       # Application settings
│   │   │   ├── agents.yaml       # Agent configuration
│   │   │   ├── tasks.yaml        # Task configuration
│   │   │   └── safety_rules.yaml # Safety rules
│   │   │
│   │   ├── knowledge/            # Knowledge base
│   │   │   ├── __init__.py       # Knowledge base initialization
│   │   │   ├── loader.py         # Knowledge loading utilities
│   │   │   ├── embeddings.py     # Vector embedding utilities
│   │   │   └── content/          # Content files
│   │   │       ├── methods/      # Hypnotherapy methods
│   │   │       ├── faq/          # Frequently asked questions
│   │   │       ├── techniques/   # Hypnotherapy techniques
│   │   │       └── safety/       # Safety information
│   │   │
│   │   ├── api/                  # API layer
│   │   │   ├── __init__.py       # API exports
│   │   │   ├── main.py           # FastAPI application
│   │   │   ├── routes/           # API routes
│   │   │   │   ├── __init__.py   # Route exports
│   │   │   │   ├── chat.py       # Chat endpoints
│   │   │   │   └── health.py     # Health check endpoints
│   │   │   ├── models/           # API data models
│   │   │   │   ├── __init__.py   # Model exports
│   │   │   │   ├── requests.py   # Request models
│   │   │   │   └── responses.py  # Response models
│   │   │   └── middleware/       # API middleware
│   │   │       ├── __init__.py   # Middleware exports
│   │   │       ├── logging.py    # Logging middleware
│   │   │       └── error.py      # Error handling middleware
│   │   │
│   │   ├── utils/                # Utility functions
│   │   │   ├── __init__.py       # Utility exports
│   │   │   ├── logging.py        # Logging utilities
│   │   │   ├── safety.py         # Safety utilities
│   │   │   └── validation.py     # Data validation utilities
│   │   │
│   │   ├── storage/              # Data persistence
│   │   │   ├── __init__.py       # Storage exports
│   │   │   ├── vector_store.py   # Vector database integration
│   │   │   └── conversation.py   # Conversation history storage
│   │   │
│   │   ├── main.py               # Application entry point
│   │   └── cli.py                # Command-line interface
│   │
│   └── web/                      # Web frontend (optional)
│       ├── public/               # Static assets
│       └── src/                  # React components
│
├── tests/                        # Test suites
│   ├── __init__.py               # Test initialization
│   ├── conftest.py               # Test fixtures and configuration
│   ├── unit/                     # Unit tests
│   │   ├── __init__.py           # Unit test initialization
│   │   ├── test_agents.py        # Agent tests
│   │   ├── test_tasks.py         # Task tests
│   │   └── test_tools.py         # Tool tests
│   ├── integration/              # Integration tests
│   │   ├── __init__.py           # Integration test initialization
│   │   ├── test_crew.py          # Crew integration tests
│   │   └── test_api.py           # API integration tests
│   └── e2e/                      # End-to-end tests
│       ├── __init__.py           # E2E test initialization
│       ├── test_chat_flow.py     # Chat flow tests
│       └── test_safety.py        # Safety protocol tests
│
├── scripts/                      # Utility scripts
│   ├── setup.sh                  # Setup script
│   ├── dev.sh                    # Development script
│   ├── test.sh                   # Test execution script
│   ├── build.sh                  # Build script
│   └── index_knowledge.py        # Knowledge base indexing script
│
└── docs/                         # Documentation
    ├── architecture/             # Architecture documentation
    ├── api/                      # API documentation
    ├── development/              # Development guides
    └── deployment/               # Deployment guides
```

## Key Components

### Agents

The system uses two specialized agents:

- **Client-Facing Agent** (`agents/client_agent.py`): Handles user interaction, information delivery, and maintaining a supportive tone.
- **QA/Safety Agent** (`agents/qa_agent.py`): Manages content review, safety monitoring, and intervention when needed.

### Tasks

Tasks are defined to handle specific aspects of the interaction:

- **Chat Task** (`tasks/chat_task.py`): Processes user messages and generates appropriate responses.
- **Review Task** (`tasks/review_task.py`): Reviews generated responses for safety and quality.

### Tools

Custom tools provide specialized functionality:

- **Knowledge Tool** (`tools/knowledge_tool.py`): Retrieves relevant information from the hypnotherapy knowledge base.
- **Safety Tool** (`tools/safety_tool.py`): Evaluates content for safety concerns and suggests interventions.

### Crew and Processes

The workflow is orchestrated through:

- **Hypno Crew** (`crew/hypno_crew.py`): Coordinates the agents and tasks.
- **Processes** (`crew/processes.py`): Defines the workflow for processing user queries.

### Configuration

Configuration is managed through:

- **Settings** (`config/settings.py`): Application settings loaded from environment variables.
- **YAML Files** (`config/*.yaml`): Agent and task configurations that can be modified without code changes.

### Knowledge Base

The knowledge base is organized into categories:

- **Methods**: Information about hypnotherapy methods.
- **FAQ**: Frequently asked questions and answers.
- **Techniques**: Specific hypnotherapy techniques and their applications.
- **Safety**: Information about safety considerations.

### API Layer

The API provides interfaces for:

- **Chat**: Processing user messages and returning responses.
- **Health**: Monitoring the health of the application.

## Implementation Strategy

1. **Core Components First**: 
   - Implement the basic agent and task structure
   - Set up the configuration system

2. **Knowledge Integration**: 
   - Set up the knowledge base structure
   - Implement the knowledge retrieval tool

3. **Safety Systems**: 
   - Implement the safety evaluation tool
   - Set up the QA agent workflow

4. **API Development**: 
   - Create the FastAPI application
   - Implement the chat endpoints

5. **Testing and Refinement**: 
   - Develop comprehensive tests
   - Refine the system based on test results

## File Templates

### Agent Configuration (agents.yaml)

```yaml
client_agent:
  role: "Hypnotherapy Guide"
  goal: "Provide accurate, supportive information about hypnotherapy"
  backstory: "You are an experienced guide helping people understand hypnotherapy"
  verbose: true
  allow_delegation: false
  tools:
    - HypnotherapyKnowledgeTool

qa_agent:
  role: "Hypnotherapy Safety Specialist"
  goal: "Ensure all responses are safe, ethical, and within scope"
  backstory: "You are a specialist in therapeutic safety and ethical guidelines"
  verbose: true
  allow_delegation: false
  tools:
    - SafetyEvaluationTool
```

### Task Configuration (tasks.yaml)

```yaml
chat_task:
  description: >
    Generate a supportive, informative response to the user's query about hypnotherapy.
    Focus on being educational and maintaining appropriate boundaries.
    
    User query: {user_query}
  expected_output: >
    A clear, supportive response that addresses the user's question

review_task:
  description: >
    Review the proposed response for safety concerns, scope violations, and ethical issues.
    
    User query: {user_query}
    Proposed response: {proposed_response}
  expected_output: >
    A safety analysis with recommended action and modified response if needed
```

### Main Application (main.py)

```python
import os
from dotenv import load_dotenv
from hypnobot.crew.hypno_crew import create_hypno_crew
from hypnobot.config.settings import settings
from hypnobot.api.main import create_app

# Load environment variables
load_dotenv()

def main():
    """Main application entry point"""
    # Create the hypnotherapy crew
    crew = create_hypno_crew()
    
    # Create the FastAPI application
    app = create_app(crew)
    
    # Start the API server if running directly
    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(
            app, 
            host=settings.HOST, 
            port=settings.PORT
        )

# Allow running as module or script
if __name__ == "__main__":
    main()
```

This structured approach ensures a maintainable, scalable application that follows CrewAI best practices for multi-agent systems. 