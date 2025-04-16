from src.hypnobot.tools.decorators import tool

@tool("hypnotherapy_methodology_tool")
def hypnotherapy_methodology_tool(query: str) -> str:
    """Placeholder RAG tool that simulates answering based on internal hypnotherapy docs."""
    return (
        "📚 This is a simulated response from the Hypnotherapy Methodology Knowledge Base.\n"
        "In a real implementation, this tool would search indexed documents and provide "
        "a grounded, accurate answer. Right now, it's just a placeholder.\n\n"
        f"📝 You asked: '{query}'"
    )
