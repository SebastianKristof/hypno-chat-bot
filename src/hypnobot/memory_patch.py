"""
Memory patch module to fix potential LangChain memory and tracing issues with CrewAI.

This patch prevents conflicts between LangChain's optional memory backends
and other libraries like embedchain that might be present in the environment.
"""

import os
import sys
import logging

logger = logging.getLogger(__name__)

def patch_memory():
    """
    Apply environment variable patches to ensure compatibility between CrewAI,
    LangChain memory components, and other AI libraries.
    
    This follows the recommended approach from CrewAI documentation to avoid
    potential issues when using memory=True with agents or when using Cursor
    with auto-suggestions.
    
    Returns:
        bool: True if the patch was applied successfully, False otherwise
    """
    try:
        # Set environment variables to disable LangChain's advanced tracing/memory plugins
        # and keep things default and stable
        os.environ["LANGCHAIN_HANDLER"] = "default"
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        
        # Optional: Add additional compatibility environment variables if needed
        # os.environ["LANGCHAIN_SESSION"] = ""  # Disable session tracking
        
        logger.info("Applied LangChain memory and tracing environment patches")
        return True
        
    except Exception as e:
        logger.error(f"Failed to apply memory patch: {str(e)}")
        return False 