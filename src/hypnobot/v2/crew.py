from crewai import Crew, Process
from src.hypnobot.config.agents import (
    categorizer, support_agent,
    safety_officer, writing_coach, accessibility_agent
)
from src.hypnobot.config.tasks import (
    categorization_task, initial_response_task,
    safety_check_task, writing_improvement_task,
    accessibility_task
)

crew = Crew(
    agents=[
        categorizer,
        support_agent,
        safety_officer,
        writing_coach,
        accessibility_agent
    ],
    tasks=[
        categorization_task,
        initial_response_task,
        safety_check_task,
        writing_improvement_task,
        accessibility_task
    ],
    process=Process.sequential
)
