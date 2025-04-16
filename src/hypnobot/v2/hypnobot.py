"""
HypnoBot - A hypnotherapy chatbot powered by CrewAI agents.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional, Any, List
import logging
import re
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("hypnobot.v2")

# Import CrewAI components
from crewai import Crew, Agent, Task, Process
from crewai.agent import Agent as CrewAgent
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

# Import configuration loader
from src.hypnobot.config.loader import load_yaml

class HypnoBot:
    def __init__(self, config_dir: str = "src/hypnobot/config"):
        self.config_dir = Path(config_dir)
        self.agents = self._load_agents()
        self.tasks = self._load_tasks()
        self.crew = self._build_crew()

        # Assign categorization agent and task explicitly for pre-check
        self.categorizer = self.agents.get("categorizer")
        self.categorization_task = self.tasks.get("categorization_task")
        if self.categorization_task and self.categorizer:
            self.categorization_task.agent = self.categorizer

    def _load_agents(self) -> Dict[str, Agent]:
        logger.info("Loading agents...")
        agents_data = load_yaml(self.config_dir / "agents.yaml")
        agents = {}
        for name, config in agents_data.items():
            tools = config.get("tools", [])
            agents[name] = Agent(
                role=config["role"],
                goal=config["goal"],
                backstory=config["backstory"],
                verbose=config.get("verbose", False),
                memory=config.get("memory", False),
                tools=[],  # You can inject tools later if needed
            )
        return agents

    def _load_tasks(self) -> Dict[str, Task]:
        logger.info("Loading tasks...")
        tasks_data = load_yaml(self.config_dir / "tasks.yaml")
        tasks = {}
        for name, config in tasks_data.items():
            tasks[name] = Task(
                description=config["description"],
                expected_output=config["expected_output"],
                agent=None  # Linked later in crew definition or dynamically
            )
        return tasks

    def _build_crew(self) -> Crew:
        logger.info("Assembling Crew...")
        # Define the process flow
        task_list = [
            self.tasks[name] for name in [
                "initial_response_task",
                "safety_check_task",
                "writing_improvement_task",
                "accessibility_task"
            ]
        ]
        # Dynamically assign agents to tasks if not already assigned
        for task in task_list:
            if not task.agent:
                # This assumes task name matches agent prefix (convention)
                agent_key = task.name.replace("_task", "")
                task.agent = self.agents.get(agent_key)

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
                result = self.categorization_task.execute(inputs={"user_input": user_input})
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
