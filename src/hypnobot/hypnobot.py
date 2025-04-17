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

        # Load agents and tasks (these should return actual Agent and Task instances)
        self.agents = load_agents(self.config_path / "agents.yaml")
        self.tasks = load_tasks(self.agents, self.config_path / "tasks.yaml")

        # Validate all agents are real
        for name, agent in self.agents.items():
            if not hasattr(agent, "execute_task"):
                raise TypeError(f"🚨 Agent '{name}' is not a valid CrewAI Agent instance. Got: {type(agent)}")

        # Assign categorization agent and task
        self.categorizer = self.agents["categorizer"]
        self.categorization_task = self.tasks["categorization_task"]

        if not hasattr(self.categorization_task, "execute"):
            raise TypeError(f"🚨 Categorization task is not a valid CrewAI Task instance. Got: {type(self.categorization_task)}")

        self.categorization_task.agent = self.categorizer

        logger.info(f"[TRACE INIT] categorization_task type: {type(self.categorization_task)}")
        logger.info(f"[TRACE INIT] categorizer type: {type(self.categorizer)}")

        # Assemble the crew (excluding categorization task — it runs independently)
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

        for task in task_list:
            logger.info(f"[CREW DEBUG] Task: {task.description[:40]}... Agent type: {type(task.agent)}")


        return Crew(
            agents=list(self.agents.values()),
            tasks=task_list,
            process=Process.sequential
        )


    def process_input(self, user_input: str) -> str:
        if isinstance(self.categorization_task.agent, dict):
            raise RuntimeError("🚨 categorization_task.agent is a dict — fix your agent assignment or YAML")

        try:
            # logger.info(f"Running categorization for input: {user_input}...")
            # logger.info(f"[TYPE CHECK] categorization_task type: {type(self.categorization_task)}")
            # logger.info(f"[TYPE CHECK] categorizer type: {type(self.categorizer)}")

            # logger.info(f"[TYPE CHECK] categorization_task.agent type: {type(self.categorization_task.agent)}")
            # logger.info(f"[TYPE CHECK] categorization_task.agent keys: {getattr(self.categorization_task.agent, 'keys', lambda: 'N/A')()}")

            # # result = self.categorization_task.execute({"user_input": user_input})
            # # ✅ Full correct invocation without relying on task.execute()
            # # result = self.categorizer.execute_task(self.categorization_task)
            
            # # Inject user input directly into the task
            # # self.categorization_task.inputs = {"user_input": user_input}

            # # Run the agent manually to bypass crewai.Task.execute()
            # result = self.categorizer.execute_task(self.categorization_task)

            # label = result.strip().splitlines()[0].upper()
            # logger.info(f"Categorization result: {label}")

            # if label != "APPROPRIATE":
            #     return (
            #         f"⚠️ Sorry, we cannot proceed with this inquiry.\n"
            #         f"Category: {label}\n\n"
            #         f"{result}"
            #     )

            logger.info("Executing full crew pipeline...")
            for task in self.crew.tasks:
                logger.debug(f"[FINAL CHECK] Task: {task.description[:40]}... agent type: {type(task.agent)}")

            # logger.info(f"[DEBUG] Crew.kickoff = {self.crew.kickoff}")
            final_output = self.crew.kickoff({"user_input": user_input})
            return final_output

        except Exception as e:
            logger.exception("❌ Error processing input")
            return f"⚠️ Something went wrong while processing your message: {str(e)}"
