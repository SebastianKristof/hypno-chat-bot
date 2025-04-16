def tool(name: str):
    """A simple placeholder for the CrewAI @tool decorator."""
    def wrapper(func):
        func.__tool__ = name
        return func
    return wrapper
