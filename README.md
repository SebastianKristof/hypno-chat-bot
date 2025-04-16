# HypnoBot

A hypnotherapy chatbot built with CrewAI that uses multiple specialized agents to provide supportive, ethical, and accessible hypnotherapy-related information.

## Architecture

HypnoBot v2 uses a multi-agent workflow with the following agents:

1. **Categorizer Agent** - Determines if user inquiries are appropriate for a hypnotherapy chatbot
2. **Support Agent** - Provides initial responses to relevant hypnotherapy questions
3. **Safety Officer** - Ensures responses are safe, ethical, and within scope
4. **Writing Coach** - Improves the writing style and tone
5. **Accessibility Agent** - Makes responses easy to understand for everyone

## Requirements

- Python 3.8+
- Dependencies from `requirements.txt`

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up your OpenAI API key:
   ```
   export OPENAI_API_KEY=your_api_key_here  # On Windows: set OPENAI_API_KEY=your_api_key_here
   ```
   Or create a `.env` file based on `.env.example`.

## Running the Bot

### CLI Mode

```
python -m src.hypnobot.main
```

### API Mode

Start the API server:

```
python run_api.py
```

Or with custom options:

```
python run_api.py --host 0.0.0.0 --port 5000 --reload
```

The API documentation is available at `/docs` (e.g., http://127.0.0.1:8000/docs).

#### API Endpoints

- **POST /api/chat** - Send a message to the chatbot
  Request:
  ```json
  {
    "user_input": "What is hypnotherapy?"
  }
  ```
  Response:
  ```json
  {
    "response": "Hypnotherapy is..."
  }
  ```

- **GET /api/health** - Check if the API is running

## Configuration

The bot is configured using YAML files:

- `src/hypnobot/config/agents.yaml` - Agent definitions
- `src/hypnobot/config/tasks.yaml` - Task definitions

## Future Enhancements

- RAG implementation for personalized responses
- Suggested follow-up questions feature