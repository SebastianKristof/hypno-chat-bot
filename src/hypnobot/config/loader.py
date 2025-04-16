from pathlib import Path
import yaml
from crewai import Agent, Task
from langchain_openai import ChatOpenAI

# Example: add tools here
from src.hypnobot.tools.methodology_rag_tool import hypnotherapy_methodology_tool

TOOL_REGISTRY = {
    "hypnotherapy_methodology_tool": hypnotherapy_methodology_tool
}

def load_yaml(path: str | Path) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)

def load_agents(path='src/hypnobot/config/agents.yaml') -> dict:
    raw_agents = load_yaml(path)
    agents = {}
    for name, config in raw_agents.items():
        tools = config.get("tools", [])
        tool_instances = [TOOL_REGISTRY[t] for t in tools]

        agent = Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            verbose=config.get("verbose", False),
            memory=config.get("memory", False),
            tools=tool_instances,
            llm=ChatOpenAI(model="gpt-4", temperature=0.2)
        )
        agents[name] = agent
    return agents

def load_tasks(agents: dict, path="src/hypnobot/config/tasks.yaml") -> dict:
    import yaml
    from pathlib import Path

    with open(Path(path), "r") as f:
        raw_tasks = yaml.safe_load(f)

    tasks = {}
    for name, config in raw_tasks.items():
        agent_key = config.get("agent")
        task = Task(
            description=config["description"],
            expected_output=config["expected_output"],
            agent=agents.get(agent_key) if agent_key else None
        )
        tasks[name] = task
        print(f"[LOADER] Loaded task '{name}' as {type(task)}")
    return tasks


