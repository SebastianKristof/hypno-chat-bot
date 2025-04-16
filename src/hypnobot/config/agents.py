import os
from pathlib import Path
from .config_loader import ConfigLoader
from crewai import Agent

# Get the absolute path to the agents.yaml file
BASE_DIR = Path(__file__).resolve().parent
AGENTS_CONFIG_PATH = os.path.join(BASE_DIR, 'agents.yaml')

# Load the agents configuration
agent_config = ConfigLoader.load_yaml(AGENTS_CONFIG_PATH)

# Create agent instances
categorizer = Agent(
    role=agent_config['categorizer']['role'],
    goal=agent_config['categorizer']['goal'],
    backstory=agent_config['categorizer']['backstory'],
    verbose=True
)

support_agent = Agent(
    role=agent_config['support_agent']['role'],
    goal=agent_config['support_agent']['goal'],
    backstory=agent_config['support_agent']['backstory'],
    verbose=True
)

safety_officer = Agent(
    role=agent_config['safety_officer']['role'],
    goal=agent_config['safety_officer']['goal'],
    backstory=agent_config['safety_officer']['backstory'],
    verbose=True
)

writing_coach = Agent(
    role=agent_config['writing_coach']['role'],
    goal=agent_config['writing_coach']['goal'],
    backstory=agent_config['writing_coach']['backstory'],
    verbose=True
)

accessibility_agent = Agent(
    role=agent_config['accessibility_agent']['role'],
    goal=agent_config['accessibility_agent']['goal'],
    backstory=agent_config['accessibility_agent']['backstory'],
    verbose=True
) 