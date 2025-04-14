import os
import re
import yaml
from typing import Dict, Any, List, Optional, Tuple

from crewai.tools import BaseTool

from hypnobot.utils.logging import get_logger

logger = get_logger(__name__)

class SafetyEvaluationTool(BaseTool):
    """Tool for evaluating content for safety concerns."""
    
    name: str = "SafetyEvaluationTool"
    description: str = """
    Evaluates content for safety concerns related to hypnotherapy discussions.
    Use this tool to assess whether content meets safety guidelines and ethical standards.
    Input should be a message to evaluate.
    Output will be a safety analysis with level (0-4) and recommendations.
    """
    
    def __init__(self):
        """Initialize the safety evaluation tool."""
        super().__init__()
        self.config_path = os.path.join(
            os.path.dirname(__file__), "..", "config", "safety_rules.yaml"
        )
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load the safety configuration from YAML."""
        try:
            with open(self.config_path, "r") as file:
                return yaml.safe_load(file)
        except Exception as e:
            logger.error(f"Error loading safety config: {e}")
            # Return a minimal default configuration
            return {
                "intervention_levels": {
                    f"level_{i}": {
                        "name": f"Level {i}",
                        "description": f"Level {i} safety",
                        "action": "approve" if i == 0 else "adjust",
                    }
                    for i in range(5)
                },
                "safety_triggers": {
                    "crisis_indicators": {
                        "description": "Crisis content",
                        "severity": 4,
                        "examples": ["suicide", "kill myself"],
                    }
                },
                "crisis_resources": {
                    "emergency": {
                        "name": "Emergency Services",
                        "contact": "911",
                    }
                },
            }
    
    def _get_intervention_level(self, content: str) -> Tuple[int, List[str], str]:
        """Determine the appropriate intervention level for the content.
        
        Args:
            content: The content to evaluate.
            
        Returns:
            Tuple containing:
                - Intervention level (0-4)
                - List of triggered keywords
                - Action to take
        """
        # Default to level 0 (no intervention)
        level = 0
        triggers = []
        action = "approve"
        
        # Check for triggers
        for trigger_key, trigger_info in self.config.get("safety_triggers", {}).items():
            severity = trigger_info.get("severity", 0)
            examples = trigger_info.get("examples", [])
            
            # Check if any examples match the content
            for example in examples:
                pattern = r'\b' + re.escape(example.lower()) + r'\b'
                if re.search(pattern, content.lower()):
                    triggers.append(example)
                    level = max(level, severity)
        
        # Get action based on level
        intervention_level = self.config.get("intervention_levels", {}).get(f"level_{level}", {})
        action = intervention_level.get("action", "approve")
        
        return level, triggers, action
    
    def _get_crisis_resources(self) -> str:
        """Get formatted crisis resources."""
        resources = self.config.get("crisis_resources", {})
        
        if not resources:
            return "Please contact emergency services for immediate help."
        
        result = "Please reach out to these resources immediately:\n\n"
        
        for resource_key, resource_info in resources.items():
            name = resource_info.get("name", "Resource")
            contact = resource_info.get("contact", "")
            available = resource_info.get("available", "")
            
            result += f"• {name}: {contact}"
            if available:
                result += f" (available {available})"
            result += "\n"
        
        return result
    
    def _run(self, content: str) -> str:
        """Run the safety evaluation on the given content.
        
        Args:
            content: The content to evaluate for safety concerns.
            
        Returns:
            A JSON string containing the safety evaluation results.
        """
        try:
            # Determine intervention level
            level, triggers, action = self._get_intervention_level(content)
            
            # Build response
            response = {
                "safety_level": level,
                "triggers": triggers,
                "action": action,
            }
            
            # Add crisis resources for level 4
            if level == 4:
                response["crisis_resources"] = self._get_crisis_resources()
            
            # Add explanation based on level
            intervention_level = self.config.get("intervention_levels", {}).get(f"level_{level}", {})
            response["explanation"] = intervention_level.get("description", "")
            
            # Convert to formatted string for CrewAI
            result = (
                f"Safety Analysis:\n"
                f"Level: {level} - {intervention_level.get('name', '')}\n"
                f"Action: {action}\n"
            )
            
            if triggers:
                result += f"Triggers: {', '.join(triggers)}\n"
            
            if level == 4:
                result += f"\nCrisis Resources:\n{self._get_crisis_resources()}\n"
            
            result += f"\nExplanation: {intervention_level.get('description', '')}"
            
            return result
        
        except Exception as e:
            logger.error(f"Error evaluating safety: {e}")
            return (
                "Safety Analysis:\n"
                "Level: 2 - Caution\n"
                "Action: adjust\n"
                "Explanation: Unable to fully evaluate content, using cautious approach."
            ) 