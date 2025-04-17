# src/hypnobot/task_factory.py

from crewai import Task

def build_task(template: Task, **kwargs) -> Task:
    """Clone a Task and apply input formatting."""
    return Task(
        description=template.description.format(**kwargs),
        expected_output=template.expected_output,
        agent=template.agent
    )
