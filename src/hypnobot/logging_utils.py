import logging
from textwrap import shorten

logger = logging.getLogger(__name__)

def make_logging_callback(task_name: str, agent_name: str, description: str):
    def log_task_callback(task_output):
        output_str = getattr(task_output, "output", str(task_output))
        print(f"\n🧠 Agent: {agent_name}")
        print(f"📝 Task: {task_name}")
        print(f"📄 Description: {description.strip()[:100]}...")
        print(f"✅ Output:\n{output_str.strip()}\n")
    return log_task_callback
