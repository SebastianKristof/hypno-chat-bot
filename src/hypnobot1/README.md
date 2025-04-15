# HypnoBot1

A hypnotherapy chatbot implementation based on the CrewAI framework, following the approach from the Jupiter notebook customer support example.

## Overview

This implementation uses a crew-based approach with two specialized agents:

1. **Hypnotherapy Guide**: Provides accurate, ethical, and supportive information about hypnotherapy
2. **Safety Specialist**: Reviews responses to ensure they adhere to ethical guidelines and safety standards

## Key Features

- YAML-based configuration for agents and tasks
- Sequential processing of user inquiries
- Two-stage review process (initial response + safety review)
- Structured result parsing
- Memory-enabled crews for context retention

## Implementation Details

### Agents

Agents are configured in `config/agents.yaml` with:
- Role
- Goal
- Backstory
- LLM configuration
- Delegation settings

### Tasks

Tasks are defined in `config/tasks.yaml` with:
- Description templates
- Expected output formats
- Agent assignments
- Tool configurations (if any)

### Workflow

1. User message is received
2. Hypnotherapy Guide agent responds to the inquiry
3. Safety Specialist reviews and potentially modifies the response
4. Structured result is returned with:
   - Original response
   - Final (potentially modified) response
   - Safety level assessment (0-4)
   - Metadata about modifications

## Usage

```python
from hypnobot1 import HypnoBot1Crew

# Initialize the crew
hypnobot = HypnoBot1Crew()

# Process a user message
result = hypnobot.process_message(
    user_message="What is hypnotherapy?",
    user_name="User"
)

# Access the results
original_response = result["original_response"]
final_response = result["final_response"]
safety_level = result["safety_level"]
modifications = result["metadata"].get("modifications", "")
```

## Testing

Run the test script to verify the implementation:

```bash
python scripts/test_hypnobot1.py
```

## Differences from Original HypnoBot

- Uses CrewAI's recommended Crew setup pattern
- Defines tasks right before execution instead of using task creators
- Employs sequential task processing with clear input/output flow
- Utilizes memory-enabled crews for better context retention
- Maintains the same YAML configuration approach 