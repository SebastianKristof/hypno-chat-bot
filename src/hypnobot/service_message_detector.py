"""
Service message detection for output validation
"""

import re

# Common patterns for service/error messages from LLM providers
SERVICE_MESSAGE_PATTERNS = [
    r"reached (?:the )?limit of (?:our|your) processing time",
    r"rate limit(?:s)? (?:exceeded|reached)",
    r"try again (?:later|in a (?:few )?(?:minutes|seconds))",
    r"(?:service|api) (?:is )?(?:unavailable|not available)",
    r"please wait (?:a (?:moment|minute|second))",
    r"queue (?:is )?(?:full|at capacity)"
]

def is_service_message(text: str) -> bool:
    """
    Check if a text appears to be a service message rather than a real answer.
    
    Args:
        text: The text to analyze
    
    Returns:
        bool: True if it's likely a service message, False otherwise
    """
    if not text:
        return False
        
    # Check for common service message patterns
    for pattern in SERVICE_MESSAGE_PATTERNS:
        if re.search(pattern, text.lower()):
            return True
            
    # Additional heuristics
    text_lower = text.lower().strip()
    
    # Very short responses are suspicious
    if len(text.split()) < 15 and any(phrase in text_lower for phrase in 
                                      ["sorry", "unavailable", "try again", "limit"]):
        return True
        
    # Messages that just apologize and don't answer
    if text_lower.startswith(("sorry", "i apologize", "unfortunately")) and len(text.split()) < 25:
        return True
        
    return False 