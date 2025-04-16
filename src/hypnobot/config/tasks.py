import os
import sys
import traceback
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

# Helper function to create tasks with version-compatible signatures
def create_task(description, expected_output, agent, context=None):
    """Create a task with compatibility for different crewai versions"""
    try:
        # Try newer API with context parameter
        return Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
            context=context
        )
    except TypeError:
        # Try older API with different parameter names
        try:
            return Task(
                description=description,
                expected_output=expected_output,
                agent=agent,
                context=context
            )
        except:
            # Fall back to minimal params
            return Task(
                description=description,
                expected_output=expected_output,
                agent=agent
            )

# Create task instances
try:
    # Create categorization task
    categorization_task = Task(
        description=task_config['categorization_task']['description'],
        expected_output=task_config['categorization_task']['expected_output'],
        agent=categorizer
    )

    # Create initial response task
    initial_response_task = Task(
        description=task_config['initial_response_task']['description'],
        expected_output=task_config['initial_response_task']['expected_output'],
        agent=support_agent,
        context=[categorization_task]  # This task depends on categorization
    )

    # Create safety check task
    safety_check_task = Task(
        description=task_config['safety_check_task']['description'],
        expected_output=task_config['safety_check_task']['expected_output'],
        agent=safety_officer,
        context=[initial_response_task]  # This task depends on initial response
    )

    # Create writing improvement task
    writing_improvement_task = Task(
        description=task_config['writing_improvement_task']['description'],
        expected_output=task_config['writing_improvement_task']['expected_output'],
        agent=writing_coach,
        context=[safety_check_task]  # This task depends on safety check
    )

    # Create accessibility task
    accessibility_task = Task(
        description=task_config['accessibility_task']['description'],
        expected_output=task_config['accessibility_task']['expected_output'],
        agent=accessibility_agent,
        context=[writing_improvement_task]  # This task depends on writing improvement
    )

    print("✅ Successfully created all tasks")
except Exception as e:
    print(f"❌ Error creating tasks: {e}")
    print(traceback.format_exc())
    
    # Try to create tasks in the most basic way
    print("Trying to create tasks with minimal parameters...")
    try:
        # Create categorization task
        categorization_task = Task(
            description=task_config['categorization_task']['description'],
            expected_output=task_config['categorization_task']['expected_output'],
            agent=categorizer
        )

        # Create initial response task
        initial_response_task = Task(
            description=task_config['initial_response_task']['description'],
            expected_output=task_config['initial_response_task']['expected_output'],
            agent=support_agent
        )

        # Create safety check task
        safety_check_task = Task(
            description=task_config['safety_check_task']['description'],
            expected_output=task_config['safety_check_task']['expected_output'],
            agent=safety_officer
        )

        # Create writing improvement task
        writing_improvement_task = Task(
            description=task_config['writing_improvement_task']['description'],
            expected_output=task_config['writing_improvement_task']['expected_output'],
            agent=writing_coach
        )

        # Create accessibility task
        accessibility_task = Task(
            description=task_config['accessibility_task']['description'],
            expected_output=task_config['accessibility_task']['expected_output'],
            agent=accessibility_agent
        )
        
        print("✅ Successfully created all tasks with minimal parameters")
    except Exception as e:
        print(f"❌ Fatal error creating tasks: {e}")
        print(traceback.format_exc())
        raise 