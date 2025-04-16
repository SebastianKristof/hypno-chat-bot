# src/hypnobot/config/loader.py

import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from crewai import Agent, Task

def load_yaml(file_path: str) -> Dict[str, Any]:
    """Load a YAML file and return its contents as a dictionary."""
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

def load_agents(file_path: str, llm=None, tools: Dict[str, Any] = None) -> Dict[str, Agent]:
    """
    Load and instantiate CrewAI agents from a YAML file.
    
    Args:
        file_path: Path to the agents YAML file
        llm: Optional LLM to use for all agents
        tools: Optional dictionary mapping tool names to tool instances
        
    Returns:
        Dictionary of agent name -> Agent instance
    """
    data = load_yaml(file_path)
    agents = {}
    
    for name, spec in data.items():
        # Get optional tools for this agent
        agent_tools = []
        if tools and 'tools' in spec:
            for tool_name in spec.get('tools', []):
                if tool_name in tools:
                    agent_tools.append(tools[tool_name])
        
        # Create the Agent instance
        agents[name] = Agent(
            role=spec.get('role', ''),
            goal=spec.get('goal', ''),
            backstory=spec.get('backstory', ''),
            verbose=spec.get('verbose', False),
            allow_delegation=spec.get('allow_delegation', True),
            tools=agent_tools,
            llm=llm
        )
    
    return agents

def load_tasks(file_path: str, agents: Dict[str, Agent], agent_task_map: Dict[str, str] = None) -> Dict[str, Task]:
    """
    Load and instantiate CrewAI tasks from a YAML file.
    
    Args:
        file_path: Path to the tasks YAML file
        agents: Dictionary of agent name -> Agent instance
        agent_task_map: Optional mapping of task names to agent names
        
    Returns:
        Dictionary of task name -> Task instance
    """
    data = load_yaml(file_path)
    tasks = {}
    
    for task_name, spec in data.items():
        # Determine which agent to use for this task
        agent = None
        
        # First check explicit agent assignment in YAML
        if 'agent' in spec and spec['agent'] in agents:
            agent = agents[spec['agent']]
        # Otherwise use the agent_task_map if provided
        elif agent_task_map and task_name in agent_task_map:
            agent_name = agent_task_map[task_name]
            if agent_name in agents:
                agent = agents[agent_name]
        
        if not agent:
            continue  # Skip tasks without an assigned agent
        
        # Create the Task instance
        tasks[task_name] = Task(
            description=spec.get('description', ''),
            expected_output=spec.get('expected_output', ''),
            agent=agent
        )
    
    return tasks

def configure_task_dependencies(tasks: Dict[str, Task], dependencies: Dict[str, List[str]]) -> None:
    """
    Configure task dependencies (context) based on the provided mapping.
    
    Args:
        tasks: Dictionary of task name -> Task instance
        dependencies: Dictionary of task name -> list of dependency task names
    """
    for task_name, dep_tasks in dependencies.items():
        if task_name in tasks:
            context = []
            for dep_name in dep_tasks:
                if dep_name in tasks:
                    context.append(tasks[dep_name])
            
            if context:
                tasks[task_name].context = context 