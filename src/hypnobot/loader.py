from pathlib import Path
import yaml
from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from src.hypnobot.logging_utils import make_logging_callback

def load_yaml(path: Path) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)

def load_agents(path: Path) -> dict:
    raw_agents = load_yaml(path)
    agents = {}
    for name, cfg in raw_agents.items():
        agents[name] = Agent(
            role=cfg["role"],
            goal=cfg["goal"],
            backstory=cfg["backstory"],
            verbose=cfg.get("verbose", False),
            memory=False,
            llm=ChatOpenAI(model="gpt-4.1-nano", temperature=0.2)
        )
    return agents


def load_tasks(agents: dict, path: str | Path = 'src/hypnobot/config/tasks.yaml') -> dict:
    raw_tasks = load_yaml(path)
    tasks = {}

    for name, config in raw_tasks.items():
        agent_key = config.get("agent")
        agent = agents.get(agent_key)

        if not agent:
            raise ValueError(f"❌ Task '{name}' references unknown agent '{agent_key}'")

        task = Task(
            description=config["description"],
            expected_output=config["expected_output"],
            agent=agent,
            callback=make_logging_callback(
                task_name=name,
                agent_name=agent.role.strip(),
                description=config["description"]
            )
        )
        tasks[name] = task
    return tasks
