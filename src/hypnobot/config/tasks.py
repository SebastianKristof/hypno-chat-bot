import os
from pathlib import Path
from .config_loader import ConfigLoader
from .agents import (
    categorizer, support_agent,
    safety_officer, writing_coach, accessibility_agent
)
from crewai import Task

# Get the absolute path to the tasks.yaml file
BASE_DIR = Path(__file__).resolve().parent
TASKS_CONFIG_PATH = os.path.join(BASE_DIR, 'tasks.yaml')

# Load the tasks configuration
task_config = ConfigLoader.load_yaml(TASKS_CONFIG_PATH)

# Create task instances
categorization_task = Task(
    description=task_config['categorization_task']['description'],
    expected_output=task_config['categorization_task']['expected_output'],
    agent=categorizer
)

initial_response_task = Task(
    description=task_config['initial_response_task']['description'],
    expected_output=task_config['initial_response_task']['expected_output'],
    agent=support_agent,
    context=[categorization_task]  # This task depends on categorization
)

safety_check_task = Task(
    description=task_config['safety_check_task']['description'],
    expected_output=task_config['safety_check_task']['expected_output'],
    agent=safety_officer,
    context=[initial_response_task]  # This task depends on initial response
)

writing_improvement_task = Task(
    description=task_config['writing_improvement_task']['description'],
    expected_output=task_config['writing_improvement_task']['expected_output'],
    agent=writing_coach,
    context=[safety_check_task]  # This task depends on safety check
)

accessibility_task = Task(
    description=task_config['accessibility_task']['description'],
    expected_output=task_config['accessibility_task']['expected_output'],
    agent=accessibility_agent,
    context=[writing_improvement_task]  # This task depends on writing improvement
) 