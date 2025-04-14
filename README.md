# Hypnotherapy Multi-Agent Chatbot

A sophisticated multi-agent chatbot system designed to support a hypnotherapy practice through client education, session planning assistance, and between-session guidance with integrated safety monitoring.

## Project Overview

This system leverages CrewAI to implement a dual-agent architecture:

1. **Client-Facing Agent**: Provides information, answers questions, and assists with hypnotherapy session planning
2. **QA/Safety Agent**: Monitors conversations for safety concerns and ensures content appropriateness

The chatbot helps clients:
- Learn about hypnotherapy methods and techniques
- Understand what to expect in sessions
- Plan their hypnotherapy journey
- Access simple relaxation techniques between sessions
- Get answers to common questions about hypnotherapy

## Key Features

- **Dynamic Multi-Agent Communication**: Agents collaborate to deliver safe, appropriate responses
- **Knowledge-Based Responses**: Vector database integration for accurate information retrieval
- **Safety-First Design**: Comprehensive safety protocols and intervention system
- **Responsive Web Interface**: Mobile-friendly chat interface for client interactions
- **Context Preservation**: Session state management for natural conversations

## Technical Architecture

The system is built on these core components:

- **CrewAI Framework**: Coordinating agent interactions and workflows
- **Vector Database**: Storing and retrieving hypnotherapy knowledge
- **Safety Rules Engine**: Monitoring and intervening in conversations
- **Web API Layer**: Connecting client interfaces to the agent system
- **Responsive Frontend**: Providing an intuitive chat experience

## Project Structure

```
src/
└── hypnobot/
    ├── agents/              # Agent definitions
    │   ├── client_agent.py  # Client-facing agent 
    │   └── qa_agent.py      # QA/Safety agent
    ├── tasks/               # Task definitions
    │   ├── chat_task.py     # User interaction task
    │   └── review_task.py   # Content review task
    ├── crew/                # Crew definitions
    │   ├── hypno_crew.py    # Main crew implementation
    │   └── processes.py     # Process-based workflow
    ├── config/              # Configuration files
    │   ├── agents.yaml      # Agent configuration
    │   ├── tasks.yaml       # Task configuration
    │   └── safety_rules.yaml# Safety rules
    ├── utils/               # Utility functions
    │   └── logging.py       # Logging utilities
    └── main.py              # Application entry point
```

## Getting Started

### Prerequisites

- Python 3.9 or higher
- OpenAI API key

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/hypno-chat-bot.git
   cd hypno-chat-bot
   ```

2. Create and activate a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables by creating a `.env` file based on `.env.example`:
   ```
   cp .env.example .env
   ```
   Then edit the `.env` file and add your OpenAI API key.

   ⚠️ **IMPORTANT**: Never commit your actual API key to the repository! The `.env` file is already in `.gitignore` to prevent accidental commits.

5. Verify your environment setup:
   ```
   python scripts/check_env.py
   ```

### Running the Chatbot

#### Interactive Mode

Run the chatbot in interactive mode:

```
python scripts/run.py -i
```

Or use the Crew approach instead of Process:

```
python scripts/run.py -i --use-crew
```

#### Process a Single Message

```
python scripts/run.py -m "What is hypnotherapy and how does it work?"
```

## Development

### Configuration

The chatbot behavior can be customized by modifying the YAML configuration files:

- `src/hypnobot/config/agents.yaml`: Agent roles, goals, and parameters
- `src/hypnobot/config/tasks.yaml`: Task descriptions and expected outputs
- `src/hypnobot/config/safety_rules.yaml`: Safety rules and intervention levels

### Adding Knowledge

To add knowledge to the chatbot:

1. Create markdown files in the `src/hypnobot/knowledge/content` directory
2. Organize content into subdirectories (methods, techniques, faq, etc.)
3. Run the indexing script to update the vector database:
   ```
   python scripts/index_knowledge.py
   ```

## License

[MIT License](LICENSE)

## Contact

For questions about this project, please contact [Your Contact Information].