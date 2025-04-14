# Safety Evaluation Tool Implementation Example

This document provides a sample implementation of the safety evaluation tool for the hypnotherapy chatbot using CrewAI's tool framework.

## Safety Tool Implementation (tools/safety_tool.py)

```python
"""
Safety evaluation tool for the hypnotherapy chatbot.
"""
from typing import Dict, Any, List, Optional, Union
import os
import re
import json
import yaml
from pathlib import Path
from crewai.tools import BaseTool
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('safety_tool')

class SafetyEvaluationTool(BaseTool):
    """
    Tool for evaluating content safety in hypnotherapy chatbot responses.
    """
    
    name: str = "SafetyEvaluationTool"
    description: str = """
    Evaluates messages and responses for safety concerns related to hypnotherapy discussions.
    Analyzes content against safety rules and recommends appropriate interventions.
    
    Input should be a JSON object with "user_message" and "proposed_response" fields.
    Output will be a safety analysis with level (0-4) and recommendations.
    
    Example input: {"user_message": "Can hypnosis cure my depression?", "proposed_response": "Hypnotherapy can be effective for helping manage symptoms of depression..."}
    """
    
    def __init__(
        self,
        rules_path: str = "src/hypnobot/config/safety_rules.yaml",
        custom_rules: Optional[List[Dict[str, Any]]] = None,
        log_interventions: bool = True,
        intervention_log_path: str = "logs/safety_interventions.jsonl",
        default_safety_level: int = 0
    ):
        """
        Initialize the safety evaluation tool.
        
        Args:
            rules_path: Path to safety rules YAML file
            custom_rules: Additional custom rules to add
            log_interventions: Whether to log interventions
            intervention_log_path: Path to intervention log file
            default_safety_level: Default safety level to use if no rules match
        """
        super().__init__()
        self.rules_path = rules_path
        self.custom_rules = custom_rules or []
        self.log_interventions = log_interventions
        self.intervention_log_path = intervention_log_path
        self.default_safety_level = default_safety_level
        
        # Load safety rules
        self.rules = self._load_safety_rules()
        
        # Create intervention log directory if needed
        if self.log_interventions:
            os.makedirs(os.path.dirname(self.intervention_log_path), exist_ok=True)
    
    def _load_safety_rules(self) -> List[Dict[str, Any]]:
        """
        Load safety rules from YAML file and custom rules.
        
        Returns:
            List of safety rule dictionaries
        """
        rules = []
        
        # Load rules from file if it exists
        if os.path.exists(self.rules_path):
            try:
                with open(self.rules_path, 'r', encoding='utf-8') as file:
                    file_rules = yaml.safe_load(file)
                    if isinstance(file_rules, dict) and 'rules' in file_rules:
                        rules.extend(file_rules['rules'])
                    elif isinstance(file_rules, list):
                        rules.extend(file_rules)
            except Exception as e:
                logger.error(f"Error loading safety rules from {self.rules_path}: {e}")
        
        # Add custom rules
        if self.custom_rules:
            rules.extend(self.custom_rules)
        
        # If no rules found, add a default emergency rule
        if not rules:
            rules.append({
                'rule_id': 'emergency_default',
                'category': 'crisis',
                'description': 'Default emergency rule for crisis detection',
                'priority': 1,
                'triggers': {
                    'keywords': ['suicide', 'kill myself', 'want to die', 'end my life', 'harm myself']
                },
                'thresholds': {
                    'confidence_min': 0.8,
                    'severity_level': 'critical'
                },
                'actions': {
                    'action_type': 'escalate',
                    'response_template': "I notice you've mentioned something concerning. This chatbot isn't equipped to provide crisis support. Please contact a mental health professional immediately or call the crisis helpline at 988 (US)."
                }
            })
        
        return rules
    
    def _evaluate_against_rules(
        self, 
        user_message: str, 
        proposed_response: str
    ) -> Dict[str, Any]:
        """
        Evaluate content against safety rules.
        
        Args:
            user_message: The user's message
            proposed_response: The proposed bot response
            
        Returns:
            Safety analysis result
        """
        # Default safety result (no issues)
        safety_result = {
            'safety_level': self.default_safety_level,
            'triggers': [],
            'matching_rules': [],
            'intervention_type': 'none',
            'reasoning': 'No safety concerns detected.'
        }
        
        # Track highest safety level found
        highest_safety_level = self.default_safety_level
        highest_priority_rule = None
        matching_rules = []
        
        # Check all rules
        for rule in self.rules:
            rule_id = rule.get('rule_id', 'unknown')
            
            # Check rule triggers against user message
            user_triggers = self._check_triggers(user_message, rule.get('triggers', {}))
            response_triggers = self._check_triggers(proposed_response, rule.get('triggers', {}))
            
            # Combine triggers
            all_triggers = list(set(user_triggers + response_triggers))
            
            # If triggers found, evaluate rule
            if all_triggers:
                # Get rule severity level
                severity_str = rule.get('thresholds', {}).get('severity_level', 'low')
                severity_map = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
                severity_level = severity_map.get(severity_str, 1)
                
                # Record rule match
                rule_match = {
                    'rule_id': rule_id,
                    'category': rule.get('category', 'unknown'),
                    'severity_level': severity_level,
                    'triggers': all_triggers,
                    'action_type': rule.get('actions', {}).get('action_type', 'none')
                }
                matching_rules.append(rule_match)
                
                # Update highest safety level if this rule has higher severity
                if severity_level > highest_safety_level:
                    highest_safety_level = severity_level
                    
                    # Store highest priority rule
                    priority = rule.get('priority', 0)
                    if highest_priority_rule is None or priority > highest_priority_rule.get('priority', 0):
                        highest_priority_rule = rule
        
        # If any rules matched, update safety result
        if matching_rules:
            # Determine intervention type based on safety level
            intervention_type = 'none'
            if highest_safety_level == 1:
                intervention_type = 'adjust'
            elif highest_safety_level == 2:
                intervention_type = 'redirect'
            elif highest_safety_level == 3:
                intervention_type = 'block'
            elif highest_safety_level >= 4:
                intervention_type = 'escalate'
            
            # Get all unique triggers
            all_triggers = []
            for rule in matching_rules:
                all_triggers.extend(rule['triggers'])
            all_triggers = list(set(all_triggers))
            
            # Update safety result
            safety_result.update({
                'safety_level': highest_safety_level,
                'triggers': all_triggers,
                'matching_rules': matching_rules,
                'intervention_type': intervention_type,
                'reasoning': f"Safety concerns detected. Matched {len(matching_rules)} rules with highest severity level {highest_safety_level}."
            })
            
            # Add response template if available from highest priority rule
            if highest_priority_rule and 'actions' in highest_priority_rule:
                actions = highest_priority_rule['actions']
                if 'response_template' in actions:
                    safety_result['suggested_response'] = actions['response_template']
                    
                # Add escalation contact if applicable
                if intervention_type == 'escalate' and 'escalation_contact' in actions:
                    safety_result['escalation_contact'] = actions['escalation_contact']
        
        return safety_result
    
    def _check_triggers(self, text: str, triggers: Dict[str, Any]) -> List[str]:
        """
        Check text against rule triggers.
        
        Args:
            text: Text to check
            triggers: Trigger definitions
            
        Returns:
            List of matched trigger strings
        """
        matched_triggers = []
        
        # Normalize text for case-insensitive matching
        normalized_text = text.lower()
        
        # Check keywords
        if 'keywords' in triggers:
            for keyword in triggers['keywords']:
                # Simple keyword matching
                if keyword.lower() in normalized_text:
                    matched_triggers.append(keyword)
        
        # Check regex patterns
        if 'patterns' in triggers:
            for pattern in triggers['patterns']:
                try:
                    if re.search(pattern, text, re.IGNORECASE):
                        matched_triggers.append(f"pattern:{pattern}")
                except Exception as e:
                    logger.error(f"Error in regex pattern '{pattern}': {e}")
        
        return matched_triggers
    
    def _generate_intervention_response(
        self,
        user_message: str,
        proposed_response: str,
        safety_result: Dict[str, Any]
    ) -> str:
        """
        Generate an appropriate intervention response based on safety analysis.
        
        Args:
            user_message: The user's message
            proposed_response: The originally proposed response
            safety_result: Safety analysis result
            
        Returns:
            Final response after intervention (if needed)
        """
        intervention_type = safety_result.get('intervention_type', 'none')
        
        # No intervention needed
        if intervention_type == 'none':
            return proposed_response
        
        # Use suggested response if provided
        if 'suggested_response' in safety_result:
            return safety_result['suggested_response']
        
        # Apply appropriate intervention based on type
        if intervention_type == 'adjust':
            # Minor adjustment - add disclaimer
            return f"{proposed_response}\n\nPlease note that hypnotherapy is a complementary approach and works best alongside conventional treatments. Results vary between individuals, and it's always recommended to consult with qualified healthcare professionals."
        
        elif intervention_type == 'redirect':
            # Redirect to appropriate information
            return "I understand your interest in this topic. However, I'd like to clarify that hypnotherapy is most effective as a complementary approach rather than a standalone treatment for medical or psychological conditions. It works best when used alongside conventional treatments under professional guidance.\n\nWould you like to know more about what hypnotherapy can help with and what a typical session involves?"
        
        elif intervention_type == 'block':
            # Block inappropriate content
            return "I understand you're seeking information, but I need to clarify that hypnotherapy has specific applications and limitations. It's not appropriate for treating serious medical or psychological conditions without professional oversight, and ethical guidelines prevent using hypnosis in ways that might influence others without their consent.\n\nI'd be happy to discuss how hypnotherapy might support your wellness goals in an appropriate and ethical way. Would that be helpful?"
        
        elif intervention_type == 'escalate':
            # Provide crisis resources
            return "I notice you've mentioned something concerning. This chatbot isn't equipped to provide crisis support. Please contact a mental health professional immediately or call the crisis helpline at 988 (US) where trained counselors are available 24/7. Your well-being is important, and help is available."
        
        # Fallback response if something goes wrong
        return "I appreciate your question, but I want to make sure I provide accurate and helpful information. Hypnotherapy is a complementary approach that works best alongside appropriate professional care. Would you like to discuss how hypnotherapy might be helpful as part of a broader approach to your well-being?"
    
    def _log_intervention(
        self,
        user_message: str,
        proposed_response: str,
        safety_result: Dict[str, Any],
        final_response: str
    ) -> None:
        """
        Log safety intervention for review.
        
        Args:
            user_message: The user's message
            proposed_response: The originally proposed response
            safety_result: Safety analysis result
            final_response: Final response after intervention
        """
        if not self.log_interventions:
            return
        
        try:
            # Create log entry
            log_entry = {
                'timestamp': import_datetime().now().isoformat(),
                'user_message': user_message,
                'proposed_response': proposed_response,
                'safety_result': safety_result,
                'final_response': final_response
            }
            
            # Append to log file
            with open(self.intervention_log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            logger.error(f"Error logging intervention: {e}")
    
    def _run(self, input_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run the safety evaluation tool.
        
        Args:
            input_data: Either a string (for backward compatibility) or a dict with user_message and proposed_response
            
        Returns:
            Safety analysis result with intervention if needed
        """
        try:
            # Parse input
            if isinstance(input_data, str):
                # Try to parse as JSON
                try:
                    input_dict = json.loads(input_data)
                    user_message = input_dict.get('user_message', '')
                    proposed_response = input_dict.get('proposed_response', '')
                except json.JSONDecodeError:
                    # Assume input is the proposed response and user message is empty
                    user_message = ''
                    proposed_response = input_data
            else:
                # Input is already a dict
                user_message = input_data.get('user_message', '')
                proposed_response = input_data.get('proposed_response', '')
            
            # Evaluate content against safety rules
            safety_result = self._evaluate_against_rules(user_message, proposed_response)
            
            # Generate appropriate response based on safety result
            final_response = self._generate_intervention_response(
                user_message, proposed_response, safety_result
            )
            
            # Log intervention if needed
            if safety_result.get('intervention_type', 'none') != 'none':
                self._log_intervention(
                    user_message, proposed_response, safety_result, final_response
                )
            
            # Return complete result
            return {
                'safety_analysis': safety_result,
                'final_response': final_response
            }
            
        except Exception as e:
            # Handle errors
            logger.error(f"Error in safety evaluation: {e}")
            return {
                'safety_analysis': {
                    'safety_level': 2,  # Medium safety level as precaution
                    'triggers': [],
                    'intervention_type': 'adjust',
                    'reasoning': f"Error during safety evaluation: {str(e)}"
                },
                'final_response': f"{proposed_response}\n\nPlease note that hypnotherapy is a complementary approach and works best alongside conventional treatments."
            }
    
    async def _arun(self, input_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Async version of _run.
        
        Args:
            input_data: Input data for evaluation
            
        Returns:
            Safety analysis result with intervention if needed
        """
        return self._run(input_data)

# Helper function to create datetime (to avoid circular imports in _log_intervention)
def import_datetime():
    from datetime import datetime
    return datetime

# Helper function to create the tool
def create_safety_evaluation_tool(
    rules_path: str = None,
    custom_rules: Optional[List[Dict[str, Any]]] = None,
    log_interventions: bool = True
) -> SafetyEvaluationTool:
    """
    Create a configured SafetyEvaluationTool instance.
    
    Args:
        rules_path: Path to safety rules YAML file
        custom_rules: Additional custom rules to add
        log_interventions: Whether to log interventions
        
    Returns:
        Configured SafetyEvaluationTool instance
    """
    # Use default paths if not provided
    if rules_path is None:
        rules_path = os.environ.get(
            "SAFETY_RULES_PATH",
            "src/hypnobot/config/safety_rules.yaml"
        )
    
    return SafetyEvaluationTool(
        rules_path=rules_path,
        custom_rules=custom_rules,
        log_interventions=log_interventions
    )
```

## Sample Safety Rules Configuration (config/safety_rules.yaml)

```yaml
# Safety rules for the hypnotherapy chatbot
rules:
  - rule_id: crisis_detection
    category: crisis
    description: "Detects potential mental health crisis situations"
    priority: 1
    triggers:
      keywords:
        - "suicide"
        - "harm myself"
        - "kill myself"
        - "end my life"
        - "want to die"
      patterns:
        - "(?i)\\b(feel|feeling)\\s+(suicidal|hopeless)\\b"
    thresholds:
      confidence_min: 0.7
      severity_level: "critical"
    actions:
      action_type: "escalate"
      response_template: "I notice you've mentioned something concerning. This chatbot isn't equipped to provide crisis support. Please contact a mental health professional immediately or call the crisis helpline at 988 (US) where trained counselors are available 24/7. Your life matters, and help is available."
      escalation_contact: "support@hypnopractice.com"

  - rule_id: medical_advice
    category: scope_limitation
    description: "Prevents the system from providing medical advice"
    priority: 2
    triggers:
      keywords:
        - "diagnose"
        - "prescription"
        - "cure my"
        - "treat my"
      patterns:
        - "(?i)\\b(can|could|will|would)\\s+(hypnotherapy|hypnosis|it)\\s+(cure|treat|heal)\\b"
    thresholds:
      confidence_min: 0.6
      severity_level: "medium"
    actions:
      action_type: "redirect"
      response_template: "I understand you're asking about treating a medical condition with hypnotherapy. While hypnotherapy can be a complementary approach for some conditions, it's important to understand that it's not considered a standalone treatment or cure. Hypnotherapy works best alongside traditional medical treatments under the guidance of healthcare professionals. Would you like to know more about how hypnotherapy might complement conventional treatments?"

  - rule_id: controlling_others
    category: ethical_practice
    description: "Prevents discussion of using hypnosis to control others"
    priority: 2
    triggers:
      keywords:
        - "control"
        - "manipulate"
        - "make them"
        - "make someone"
      patterns:
        - "(?i)\\b(hypnotize|hypnotise)\\s+(someone|them|him|her|my)\\b"
        - "(?i)\\b(make|get)\\s+(someone|them|him|her|my)\\s+(do|feel|think)\\b"
    thresholds:
      confidence_min: 0.7
      severity_level: "high"
    actions:
      action_type: "block"
      response_template: "I understand you're curious about hypnosis, but I need to clarify that ethical hypnotherapy is always based on consent and cannot be used to control someone else's behavior or choices. Hypnotherapy is a collaborative process focused on helping individuals make positive changes they desire for themselves. Would you like to learn more about the ethical applications of hypnotherapy instead?"

  - rule_id: unrealistic_expectations
    category: scope_limitation
    description: "Manages unrealistic expectations about hypnotherapy results"
    priority: 3
    triggers:
      keywords:
        - "guarantee"
        - "promise"
        - "definitely work"
        - "completely cure"
      patterns:
        - "(?i)\\b(will it|does it)\\s+(definitely|absolutely|completely|totally)\\s+(work|cure|fix|solve)\\b"
    thresholds:
      confidence_min: 0.5
      severity_level: "low"
    actions:
      action_type: "adjust"
      response_template: "Hypnotherapy can be helpful for many people, but it's important to understand that results vary between individuals. While many clients report positive outcomes, hypnotherapy is not a guaranteed cure or solution for everyone. It often works best as part of a comprehensive approach to well-being, and multiple sessions are typically needed to see meaningful changes."

  - rule_id: past_life_regression
    category: ethical_practice
    description: "Provides appropriate context for past life regression inquiries"
    priority: 4
    triggers:
      keywords:
        - "past life"
        - "previous life"
        - "reincarnation"
        - "past lives regression"
      patterns:
        - "(?i)\\b(remember|recall|access)\\s+(my|a)\\s+(past|previous)\\s+life\\b"
    thresholds:
      confidence_min: 0.6
      severity_level: "medium"
    actions:
      action_type: "redirect"
      response_template: "Past life regression is considered an experimental application of hypnotherapy. While some hypnotherapists offer this service, it's important to understand that it's not scientifically validated, and the experiences during these sessions are often viewed as metaphorical rather than literal memories. If you're interested in this area, it's best approached with an open but critical mindset, focusing on the potential insights rather than factual historical accuracy."
```

## Using the Safety Tool with CrewAI Agents

The safety tool can be integrated with CrewAI agents to ensure content safety:

```python
from crewai import Agent
from hypnobot.tools.safety_tool import create_safety_evaluation_tool

# Create the safety tool
safety_tool = create_safety_evaluation_tool()

# Create a QA agent with the safety tool
qa_agent = Agent(
    role="Hypnotherapy Safety Specialist",
    goal="Ensure all responses are safe, ethical, and within scope",
    backstory="You are a specialist in therapeutic safety and ethical guidelines for hypnotherapy.",
    verbose=True,
    tools=[safety_tool]
)
```

## Tool Usage in Agent Workflows

When reviewing client-facing agent responses, the QA agent can use the safety tool to evaluate content:

```
# Input from client-facing agent
USER: "Can hypnosis cure my depression?"
CLIENT AGENT: "Hypnotherapy can be effective for helping manage symptoms of depression by addressing negative thought patterns and promoting relaxation."

# QA agent review using safety tool
QA AGENT THOUGHT: I need to evaluate this response for safety and accuracy. I'll use the safety tool to check if it violates any guidelines.

TOOL CALL: SafetyEvaluationTool
TOOL INPUT: {
    "user_message": "Can hypnosis cure my depression?",
    "proposed_response": "Hypnotherapy can be effective for helping manage symptoms of depression by addressing negative thought patterns and promoting relaxation."
}
TOOL OUTPUT: {
    "safety_analysis": {
        "safety_level": 2,
        "triggers": ["cure my", "pattern:(?i)\\b(can|could|will|would)\\s+(hypnotherapy|hypnosis|it)\\s+(cure|treat|heal)\\b"],
        "matching_rules": [
            {
                "rule_id": "medical_advice",
                "category": "scope_limitation",
                "severity_level": 2,
                "triggers": ["cure my", "pattern:(?i)\\b(can|could|will|would)\\s+(hypnotherapy|hypnosis|it)\\s+(cure|treat|heal)\\b"],
                "action_type": "redirect"
            }
        ],
        "intervention_type": "redirect",
        "reasoning": "Safety concerns detected. Matched 1 rules with highest severity level 2."
    },
    "final_response": "I understand you're asking about treating a medical condition with hypnotherapy. While hypnotherapy can be a complementary approach for some conditions, it's important to understand that it's not considered a standalone treatment or cure. Hypnotherapy works best alongside traditional medical treatments under the guidance of healthcare professionals. Would you like to know more about how hypnotherapy might complement conventional treatments?"
}

QA AGENT RESPONSE: I need to modify the response to clarify the limitations of hypnotherapy for depression treatment. The original response doesn't sufficiently emphasize that hypnotherapy is a complementary approach rather than a standalone treatment.

FINAL RESPONSE TO USER: "Hypnotherapy can be a supportive tool for managing some symptoms associated with depression, such as stress or sleep issues. However, it's important to understand that it's not considered a standalone treatment or cure for clinical depression. Depression typically requires a comprehensive approach developed with mental health professionals, which might include therapy (such as CBT), and sometimes medication. Many people find that hypnotherapy works best as a complementary approach alongside these primary treatments. Have you been working with a healthcare provider on your depression management?"
```

## Benefits of This Approach

1. **Rule-Based Safety**: The tool uses explicit rules to identify safety concerns, making the system transparent and maintainable.

2. **Configurable Interventions**: Different types of interventions can be configured based on the severity of safety concerns.

3. **Logging and Monitoring**: Safety interventions are logged for review, allowing continuous improvement of the safety system.

4. **Multiple Detection Methods**: The tool uses both keyword matching and regex patterns for more accurate detection.

5. **Graceful Error Handling**: The tool has robust error handling to ensure the system remains operational even if issues occur.

This implementation provides a robust foundation for ensuring content safety in the hypnotherapy chatbot, allowing it to maintain appropriate boundaries and provide ethical guidance to users. 