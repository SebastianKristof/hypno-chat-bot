import os
import sys
import pytest
from pathlib import Path

# Add the project root to the system path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from src.hypnobot.config.config_loader import ConfigLoader

# Create test YAML data
TEST_AGENTS_YAML = """
test_agent:
  role: Test Agent
  goal: To test the config loader
  backstory: I am a test agent for unit testing
"""

TEST_TASKS_YAML = """
test_task:
  description: A test task for unit testing
  expected_output: Successfully completed test task
"""

class TestConfigLoader:
    """Tests for the ConfigLoader class."""

    def test_load_yaml(self, tmp_path):
        """Test the load_yaml method."""
        # Create a test YAML file
        yaml_file = tmp_path / "test_agents.yaml"
        yaml_file.write_text(TEST_AGENTS_YAML)
        
        # Load the YAML file
        yaml_data = ConfigLoader.load_yaml(str(yaml_file))
        
        # Verify the loaded data
        assert "test_agent" in yaml_data
        assert yaml_data["test_agent"]["role"] == "Test Agent"
        assert yaml_data["test_agent"]["goal"] == "To test the config loader"
        
    def test_load_yaml_file_not_found(self):
        """Test the load_yaml method with a non-existent file."""
        with pytest.raises(FileNotFoundError):
            ConfigLoader.load_yaml("non_existent_file.yaml")
    
    def test_create_agents(self, tmp_path):
        """Test the create_agents method."""
        # Create a test YAML file
        yaml_file = tmp_path / "test_agents.yaml"
        yaml_file.write_text(TEST_AGENTS_YAML)
        
        # Load the YAML file
        yaml_data = ConfigLoader.load_yaml(str(yaml_file))
        
        # Create agents
        agents = ConfigLoader.create_agents(yaml_data)
        
        # Verify the agents
        assert "test_agent" in agents
        assert agents["test_agent"].role == "Test Agent"
        assert agents["test_agent"].goal == "To test the config loader"
        assert agents["test_agent"].backstory == "I am a test agent for unit testing"
    
    def test_create_tasks(self, tmp_path, mocker):
        """Test the create_tasks method."""
        # Create a test YAML file for tasks
        tasks_file = tmp_path / "test_tasks.yaml"
        tasks_file.write_text(TEST_TASKS_YAML)
        
        # Create a test YAML file for agents
        agents_file = tmp_path / "test_agents.yaml"
        agents_file.write_text(TEST_AGENTS_YAML)
        
        # Load the YAML data
        tasks_data = ConfigLoader.load_yaml(str(tasks_file))
        agents_data = ConfigLoader.load_yaml(str(agents_file))
        
        # Create agents
        agents = ConfigLoader.create_agents(agents_data)
        
        # Mock the agent get method to avoid name mismatch error
        mock_agent = agents["test_agent"]
        mock_agents = {"test": mock_agent}
        
        # Create tasks
        tasks = ConfigLoader.create_tasks(tasks_data, mock_agents)
        
        # Verify the tasks
        assert "test_task" in tasks
        assert tasks["test_task"].description == "A test task for unit testing"
        assert tasks["test_task"].expected_output == "Successfully completed test task" 