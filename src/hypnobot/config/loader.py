from pathlib import Path
import yaml
from crewai import Agent, Task
from langchain_openai import ChatOpenAI
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

def load_tasks(agents: dict, path: str | Path = 'src/hypnobot/config/tasks.yaml') -> dict:
    raw_tasks = load_yaml(path)
    tasks = {}

    for name, config in raw_tasks.items():
        # ✅ ONLY use the key to lookup a real Agent instance
        agent_key = config.get("agent", None)

        if agent_key is not None:
            agent = agents.get(agent_key)
            if not agent:
                raise ValueError(f"❌ Task '{name}' references unknown agent '{agent_key}'")
        else:
            agent = None

        task = Task(
            description=config["description"],
            expected_output=config["expected_output"],
            agent=agent
        )
        tasks[name] = task
        print(f"[LOADER ✅] Task '{name}' → agent: {type(agent)}")
    return tasks