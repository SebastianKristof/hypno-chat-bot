from pathlib import Path
import yaml
from crewai import Agent, Task
from langchain_openai import ChatOpenAI

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

def load_tasks(agents: dict, path: Path) -> dict:
    raw_tasks = load_yaml(path)
    tasks = {}
    for name, cfg in raw_tasks.items():
        agent = agents.get(cfg.get("agent"))
        tasks[name] = Task(
            description=cfg["description"],
            expected_output=cfg["expected_output"],
            agent=agent
        )
    return tasks
