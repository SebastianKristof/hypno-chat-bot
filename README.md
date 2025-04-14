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

## Getting Started

1. Clone this repository
2. Install dependencies: `npm install`
3. Configure environment variables (see `.env.example`)
4. Run the development server: `npm run dev`

## License

[MIT License](LICENSE)

## Contact

For questions about this project, please contact [Your Contact Information].