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

## Deployment

The application supports two environment modes:

### Development Mode (default)

- Uses `.env` file for configuration
- Good for local development and testing
- Set by default when `ENVIRONMENT` is not specified

### Production Mode

- Uses environment variables directly from the hosting platform
- Recommended for deployed environments
- Set by specifying `ENVIRONMENT=production`

To run in production mode:

```bash
# Linux/macOS
export ENVIRONMENT=production
export OPENAI_API_KEY=your_api_key_here
python scripts/run.py -i

# Windows PowerShell
$env:ENVIRONMENT = "production"
$env:OPENAI_API_KEY = "your_api_key_here"
python scripts/run.py -i
```

When deploying to cloud platforms, configure these environment variables in your hosting provider's dashboard or deployment configuration.

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

# Using HypnoBot1 in Interactive Mode

To interact with HypnoBot1 in a conversational mode, you can use the `-i` or `--interactive` flag with the run_hypnobot1.py script:

```bash
python run_hypnobot1.py --interactive
```

This will start an interactive session where you can chat with HypnoBot1. Here are the available commands:

- Type your questions or messages about hypnotherapy to get responses
- Type `exit`, `quit`, or `bye` to end the conversation
- Type `clear` to start a new conversation
- Type `help` to see the instructions again

The interactive mode provides a more natural way to explore hypnotherapy topics through conversation.

## Features

- **Multilingual Support**: HypnoBot1 naturally responds in the same language as your question. Simply ask in your preferred language, and the agents will maintain that language throughout the conversation.
- **Safety Monitoring**: All responses are reviewed by a safety specialist agent to ensure they are ethical and appropriate.
- **Accurate Information**: Provides evidence-based information about hypnotherapy techniques and practices.
- **Helpful Guidance**: Offers supportive and empathetic responses while maintaining appropriate boundaries.

## Examples of questions you can ask:

- "What is hypnotherapy?"
- "How does hypnotherapy work for anxiety?"
- "Is hypnotherapy safe for everyone?"
- "What qualifications should a hypnotherapist have?"
- "Can hypnotherapy help with sleep issues?"
- "¿Qué es la hipnoterapia?" (Spanish)
- "Comment l'hypnothérapie peut-elle aider avec l'anxiété?" (French)
- "Was ist Hypnotherapie?" (German)

Each response is first generated by the Hypnotherapy Guide agent and then reviewed by the Safety & Ethics Specialist agent to ensure accuracy, ethical standards, and appropriate boundaries - all in the language of your original question.

## Running in Demo Mode

If you prefer to see a demonstration with predefined questions, simply run:

```bash
python run_hypnobot1.py
```

This will process a set of sample questions and show both the original response and the safety-reviewed final response for each one.

# Workflow Architecture

The HypnoBot1 system uses a sequential two-agent approach:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                 USER                                     │
│                                  │                                       │
│                                  ▼                                       │
│                          "Ask a question"                                │
│                        (in any language)                                 │
└───────────────────────────┬─────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────────────┐
│                       First Crew                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                 Agent: Hypnotherapy Guide                          │  │
│  │  • Processes user question in original language                    │  │
│  │  • Generates informative response in same language                 │  │
│  │  • Delivers hypnotherapy information                               │  │
│  └─────────────────────────┬───────────────────────────────────────┘  │  │
└───────────────────────────┬┴─────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────────────┐
│                       Second Crew                                        │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │            Agent: Safety & Ethics Specialist                       │  │
│  │  • Reviews hypnotherapy response                                   │  │
│  │  • Assesses safety level (0-4)                                     │  │
│  │  • Makes modifications if needed (maintaining original language)   │  │
│  │  • Provides reasoning for changes                                  │  │
│  └─────────────────────────┬───────────────────────────────────────┘  │  │
└───────────────────────────┬┴─────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────────────┐
│                       Final Response                                     │
│                (in User's Original Language)                             │
└─────────────────────────────────────────────────────────────────────────┘
```

The workflow includes these key steps:

1. **User Question**: The user asks a question in any language
2. **Primary Response Generation**: The Hypnotherapy Guide agent creates a response in the same language
3. **Safety Review**: The Safety & Ethics Specialist reviews the response
4. **Result Delivery**: The final response is delivered to the user in their original language

This architecture ensures that:
- Users can interact in their preferred language
- Content is reviewed for safety and accuracy
- The entire conversation maintains language consistency
- Language handling is managed naturally by the LLM's capabilities