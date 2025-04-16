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

### Automated Setup (Recommended)

Run the setup script to create a virtual environment and install compatible dependencies:

```bash
# Unix/macOS
./setup_env.sh

# Activate the virtual environment
source venv/bin/activate
```

### Manual Setup

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
   
   If you encounter dependency conflicts, use the compatible versions:
   ```
   pip install -r requirements-compatible.txt
   ```

4. Set up your OpenAI API key:
   ```
   export OPENAI_API_KEY=your_api_key_here  # On Windows: set OPENAI_API_KEY=your_api_key_here
   ```
   Or create a `.env` file based on `.env.example`.

## Running the Bot

### CLI Mode

You can run the bot in CLI mode using one of the following methods:

```bash
# Using the main module 
python -m src.hypnobot.main
```

or using the dedicated CLI script with more options:

```bash
# Interactive mode
./run_cli.py

# With a specific model
./run_cli.py --model gpt-4

# Process a single message and exit
./run_cli.py --single "What is hypnotherapy?"

# Verbose mode with more information
./run_cli.py -v
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

## Docker Support

For dependency isolation and easier deployment, HypnoBot can be run using Docker.

### Prerequisites
- Docker and Docker Compose installed

### Setup

1. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

2. Build and run using Docker Compose:

   ```bash
   # Run the API server
   docker-compose up hypnobot-api
   
   # Run the CLI in interactive mode
   docker-compose up hypnobot-cli
   ```

3. For custom commands with the CLI version:

   ```bash
   # Single message mode
   docker-compose run hypnobot-cli python run_cli.py --single "What is hypnotherapy?"
   
   # Different model
   docker-compose run hypnobot-cli python run_cli.py --model gpt-4
   ```

The Docker setup uses compatible versions of CrewAI and LangChain packages to avoid dependency conflicts.

## Testing

The project includes comprehensive unit and integration tests. To run the tests:

```bash
# Run all tests
python run_tests.py

# Run with verbose output
python run_tests.py -v

# Run only unit tests
python run_tests.py --unit

# Run only integration tests
python run_tests.py --integration

# Run tests with coverage report
python run_tests.py --coverage
```

The coverage report will be generated in HTML format in the `htmlcov` directory.

## Configuration

The bot is configured using YAML files:

- `src/hypnobot/config/agents.yaml` - Agent definitions
- `src/hypnobot/config/tasks.yaml` - Task definitions

## Troubleshooting

If you encounter dependency conflicts between CrewAI and LangChain packages:

1. Use the compatible versions specified in `requirements-compatible.txt`
2. Or use the Docker setup which isolates dependencies
3. For development, the setup script (`setup_env.sh`) will create a clean environment with compatible packages

## Future Enhancements

- RAG implementation for personalized responses
- Suggested follow-up questions feature