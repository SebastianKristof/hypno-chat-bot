import sys
import traceback
from crewai import Crew, Process
from pathlib import Path

# Add current directory to path if needed
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

# Add parent directory to path if needed
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))

try:
    # Try relative imports first
    from config.agents import (
        categorizer, support_agent,
        safety_officer, writing_coach, accessibility_agent
    )
    from config.tasks import (
        categorization_task, initial_response_task,
        safety_check_task, writing_improvement_task,
        accessibility_task
    )
    print("✅ Successfully imported agents and tasks in crew.py")
except ImportError as e:
    print(f"❌ Error importing from relative path in crew.py: {e}")
    
    try:
        # Fall back to absolute imports
        from src.hypnobot.config.agents import (
            categorizer, support_agent,
            safety_officer, writing_coach, accessibility_agent
        )
        from src.hypnobot.config.tasks import (
            categorization_task, initial_response_task,
            safety_check_task, writing_improvement_task,
            accessibility_task
        )
        print("✅ Successfully imported using absolute path in crew.py")
    except ImportError as e:
        print(f"❌ Error importing from absolute path in crew.py: {e}")
        print(traceback.format_exc())
        raise RuntimeError("Failed to import required modules in crew.py")

# Set proper task dependencies to create a chain
# This is the CrewAI way to chain tasks
try:
    # First task has no dependencies
    
    # Set dependencies for the other tasks
    initial_response_task.human_input = False
    initial_response_task.dependencies = [categorization_task]
    
    safety_check_task.human_input = False
    safety_check_task.dependencies = [initial_response_task]
    
    writing_improvement_task.human_input = False  
    writing_improvement_task.dependencies = [safety_check_task]
    
    accessibility_task.human_input = False
    accessibility_task.dependencies = [writing_improvement_task]
    
    print("✅ Successfully set task dependencies")
except Exception as e:
    print(f"❌ Warning: Could not set task dependencies: {e}")
    print(traceback.format_exc())

# Initialize the crew with sequential workflow
try:
    crew = Crew(
        agents=[
            categorizer,
            support_agent,
            safety_officer, 
            writing_coach,
            accessibility_agent
        ],
        tasks=[
            categorization_task,
            initial_response_task,
            safety_check_task,
            writing_improvement_task,
            accessibility_task
        ],
        process=Process.sequential,
        verbose=True
    )
    print("✅ Successfully initialized crew in crew.py")
except Exception as e:
    print(f"❌ Error initializing crew in crew.py: {e}")
    print(traceback.format_exc())
