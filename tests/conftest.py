import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project root to the system path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

@pytest.fixture
def mock_openai_env():
    """Mock OpenAI environment variables."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
        yield

@pytest.fixture
def mock_llm():
    """Mock the LLM for testing."""
    with patch('langchain_openai.ChatOpenAI') as mock:
        mock_llm_instance = MagicMock()
        mock.return_value = mock_llm_instance
        yield mock_llm_instance

@pytest.fixture
def mock_crew():
    """Mock the Crew for testing."""
    with patch('crewai.Crew') as mock:
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = "Test response"
        mock.return_value = mock_crew_instance
        yield mock_crew_instance

@pytest.fixture
def mock_agent():
    """Mock the Agent for testing."""
    with patch('crewai.Agent') as mock:
        mock_agent_instance = MagicMock()
        mock.return_value = mock_agent_instance
        yield mock_agent_instance

@pytest.fixture
def mock_task():
    """Mock the Task for testing."""
    with patch('crewai.Task') as mock:
        mock_task_instance = MagicMock()
        mock.return_value = mock_task_instance
        yield mock_task_instance 