agents = [
    Agent(
        role="Categorization Agent",
        goal="Analyze user messages for appropriate categorization",
        backstory="You analyze user questions for content and intent, determining if they are appropriate.",
        verbose=True,
        tools=[categorize_input],
        allow_delegation=False,
        llm=llm_config
    ),
    Agent(
        role="Initial Response Agent",
        goal="Create an initial empathetic hypnosis response",
        backstory="You're an expert in hypnotherapy techniques creating initial responses.",
        verbose=True,
        tools=[create_initial_response],
        allow_delegation=False,
        llm=llm_config
    ),
    Agent(
        role="Safety Agent",
        goal="Ensure responses are safe, ethical, and legal",
        backstory="You analyze responses to ensure they meet safety, ethical, and legal standards.",
        verbose=True,
        tools=[review_safety],
        allow_delegation=False,
        llm=llm_config
    ),
    Agent(
        role="Writing Enhancement Agent",
        goal="Improve flow, clarity, and impact of responses",
        backstory="You're an expert writer who improves the quality of therapeutic content.",
        verbose=True,
        tools=[enhance_writing],
        allow_delegation=False,
        llm=llm_config
    ),
    Agent(
        role="Accessibility Agent",
        goal="Ensure responses are accessible to all users",
        backstory="You refine content to be accessible to users of all backgrounds.",
        verbose=True,
        tools=[improve_accessibility],
        allow_delegation=False,
        llm=llm_config
    )
]

# Configure tasks with appropriate dependencies
tasks = [
    Task(
        description="Categorize the input for appropriateness",
        agent=agents[0],
        expected_output="A tuple of (is_appropriate, category, explanation)",
        async_execution=False
    ),
    Task(
        description="Create an initial response based on the user's query",
        agent=agents[1],
        expected_output="An initial therapeutic response",
        async_execution=False,
        context={"user_input": "{user_input}"}
    ),
    Task(
        description="Review the initial response for safety and ethical concerns",
        agent=agents[2],
        expected_output="A safety-checked response",
        async_execution=False,
        context={
            "user_input": "{user_input}",
            "initial_response": "{task_1}"
        }
    ),
    Task(
        description="Enhance the writing quality of the response",
        agent=agents[3],
        expected_output="An improved, well-written response",
        async_execution=False,
        context={
            "user_input": "{user_input}",
            "safety_checked_response": "{task_2}" 
        }
    ),
    Task(
        description="Make the response more accessible and suitable for all audiences",
        agent=agents[4],
        expected_output="The final, accessible therapeutic response",
        async_execution=False,
        context={
            "user_input": "{user_input}",
            "improved_response": "{task_3}"
        }
    )
] 