import yaml
import os
from crewai import Agent, Task
from typing import Dict, List, Any, Union

class ConfigLoader:
    """
    Loads YAML configuration files for CrewAI agents and tasks.
    """
    
    @staticmethod
    def load_yaml(file_path: str) -> Dict[str, Any]:
        """Load a YAML file and return its contents as a dictionary."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Config file not found: {file_path}")
        
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    
    @staticmethod
    def create_agents(yaml_config: Dict[str, Dict[str, str]], tools: Dict[str, Any] = None) -> Dict[str, Agent]:
        """
        Create CrewAI agents from YAML configuration.
        
        Args:
            yaml_config: Dictionary containing agent configurations
            tools: Optional dictionary of tools to assign to agents
            
        Returns:
            Dictionary of agent name -> Agent object
        """
        agents = {}
        
        for agent_name, agent_config in yaml_config.items():
            agent_tools = []
            if tools and agent_name in tools:
                agent_tools = tools[agent_name]
                
            agents[agent_name] = Agent(
                role=agent_config.get('role', ''),
                goal=agent_config.get('goal', ''),
                backstory=agent_config.get('backstory', ''),
                verbose=True,
                tools=agent_tools
            )
        
        return agents
    
    @staticmethod
    def create_tasks(yaml_config: Dict[str, Dict[str, str]], 
                     agents: Dict[str, Agent],
                     task_context: Dict[str, List[str]] = None) -> Dict[str, Task]:
        """
        Create CrewAI tasks from YAML configuration.
        
        Args:
            yaml_config: Dictionary containing task configurations
            agents: Dictionary of agent name -> Agent object
            task_context: Optional dictionary of task name -> list of dependency task names
            
        Returns:
            Dictionary of task name -> Task object
        """
        tasks = {}
        
        # First pass: create all tasks without context
        for task_name, task_config in yaml_config.items():
            # Get the agent for this task - assuming task names match agent names
            agent = agents.get(task_name.replace('_task', ''))
            
            if not agent:
                raise ValueError(f"No matching agent found for task: {task_name}")
                
            tasks[task_name] = Task(
                description=task_config.get('description', ''),
                expected_output=task_config.get('expected_output', ''),
                agent=agent
            )
        
        # Second pass: add context dependencies if provided
        if task_context:
            for task_name, context_tasks in task_context.items():
                if task_name in tasks and context_tasks:
                    context = [tasks[t] for t in context_tasks if t in tasks]
                    tasks[task_name].context = context
                    
        return tasks 