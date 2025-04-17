import logging
from pathlib import Path
from dotenv import load_dotenv

from crewai import Crew, Process, Task
from src.hypnobot.loader import load_agents, load_tasks
from src.hypnobot.task_factory import build_task
from src.hypnobot.service_message_detector import is_service_message
import re
# Load environment variables
load_dotenv()


# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class HypnoBot:
    def __init__(self):
        base = Path("src/hypnobot/config")
        self.agents = load_agents(base / "agents.yaml")
        self.tasks = load_tasks(self.agents, base / "tasks.yaml")

        self.crew = Crew(
            agents=list(self.agents.values()),
            tasks=[
                self.tasks["initial_response_task"],
                self.tasks["safety_check_task"],
                self.tasks["writing_improvement_task"],
                self.tasks["accessibility_task"]
            ],
            process=Process.sequential
        )


    def process(self, user_input: str) -> str:
        logger.info(f"Input received: {user_input}")

        # Rebuild categorization task dynamically
        cat_template = self.tasks["categorization_task"]
        cat_task = build_task(cat_template, user_input=user_input)

        result = cat_task.agent.execute_task(cat_task)
        logger.info(f"Categorization raw result: {result}")

        # Check if result is a service message
        if is_service_message(result):
            logger.warning("Received service message instead of real answer for categorization")
            return "I'm having trouble processing your request right now. Please try again in a moment."

        label_line = result.strip().splitlines()[0].upper()

        logger.info(f"Categorization: {label_line}")

        if not label_line.startswith("APPROPRIATE"):
            return f"⚠️ Sorry, we cannot proceed. Category: {label_line}\n\n{result}"

        def safe_format_description(desc: str, user_input: str) -> str:
            # Replace only `{user_input}` — leave any other {xyz.output} untouched
            return re.sub(r"{user_input}", user_input, desc)

        for task in self.crew.tasks:
            task.description = safe_format_description(task.description, user_input)

        # Run the full crew
        crew_result = self.crew.kickoff()
        
        # Check if the crew result is a service message
        if is_service_message(crew_result):
            logger.warning("Received service message instead of real answer from crew")
            return "I'm having trouble processing your request right now. Please try again in a moment."
            
        return crew_result

