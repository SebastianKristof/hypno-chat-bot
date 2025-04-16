"""
HypnoBot - A hypnotherapy chatbot powered by CrewAI agents.
"""

import logging
from pathlib import Path
from crewai import Crew, Process
from src.hypnobot.config.loader import load_agents, load_tasks


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HypnoBot:
    def __init__(self):
        self.config_path = Path("src/hypnobot/config")
        self.agents = load_agents(self.config_path / "agents.yaml")
        self.tasks = load_tasks(self.agents, self.config_path / "tasks.yaml")

        # Assign categorization agent and task (fails fast if misconfigured)
        self.categorizer = self.agents["categorizer"]
        self.categorization_task = self.tasks["categorization_task"]
        self.categorization_task.agent = self.categorizer

        logger.warning(f"[TRACE INIT] categorization_task type: {type(self.categorization_task)}")


        self.crew = self._build_crew()

    def _build_crew(self) -> Crew:
        logger.info("Assembling Crew...")

        task_agent_map = {
            "initial_response_task": "support_agent",
            "safety_check_task": "safety_officer",
            "writing_improvement_task": "writing_coach",
            "accessibility_task": "accessibility_agent"
        }

        task_list = []
        for task_name, agent_key in task_agent_map.items():
            task = self.tasks[task_name]
            if not task.agent:
                task.agent = self.agents[agent_key]
            task_list.append(task)

        return Crew(
            agents=list(self.agents.values()),
            tasks=task_list,
            process=Process.sequential
        )


    def process_input(self, user_input: str) -> str:
        try:
            logger.info(f"Running categorization for input: {user_input}...")
            if not self.categorization_task or not self.categorizer:
                logger.warning("Categorizer not configured — skipping pre-check")
            else:
                result = self.categorization_task.execute({"user_input": user_input})
                label = result.strip().splitlines()[0].upper()
                logger.info(f"Categorization result: {label}")

                if label != "APPROPRIATE":
                    return (
                        f"⚠️ Sorry, we cannot proceed with this inquiry.\n"
                        f"Category: {label}\n\n"
                        f"{result}"
                    )

            logger.info("Executing full crew pipeline...")
            final_output = self.crew.kickoff(inputs={"user_input": user_input})
            return final_output

        except Exception as e:
            logger.exception("❌ Error processing input")
            return f"⚠️ Something went wrong while processing your message: {str(e)}"
