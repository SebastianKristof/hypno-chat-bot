import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import unittest
from src.hypnobot.hypnobot import HypnoBot

# Add the project root to the system path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

class TestHypnoBot:
    """Tests for the HypnoBot class."""
    
    @patch('src.hypnobot.hypnobot.ChatOpenAI')
    def test_init(self, mock_chat_openai):
        """Test the initialization of the HypnoBot class."""
        # Mock the ChatOpenAI class
        mock_chat_openai.return_value = MagicMock()
        
        # Initialize the HypnoBot
        bot = HypnoBot(model_name="gpt-3.5-turbo")
        
        # Verify the initialization
        assert bot.model_name == "gpt-3.5-turbo"
        assert mock_chat_openai.called
        assert bot.crew is not None
    
    @patch('src.hypnobot.hypnobot.ChatOpenAI')
    @patch('src.hypnobot.hypnobot.Crew')
    def test_process_input(self, mock_crew, mock_chat_openai):
        """Test the process_input method."""
        # Mock the ChatOpenAI class
        mock_chat_openai.return_value = MagicMock()
        
        # Mock the Crew class
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = "Test response"
        mock_crew.return_value = mock_crew_instance
        
        # Initialize the HypnoBot
        bot = HypnoBot()
        
        # Process an input
        response = bot.process_input("Test input")
        
        # Verify the response
        assert response == "Test response"
        mock_crew_instance.kickoff.assert_called_once_with(inputs={'user_input': 'Test input'})
    
    @patch('src.hypnobot.hypnobot.ChatOpenAI')
    def test_format_task_template(self, mock_chat_openai):
        """Test the format_task_template method."""
        # Mock the ChatOpenAI class
        mock_chat_openai.return_value = MagicMock()
        
        # Initialize the HypnoBot
        bot = HypnoBot()
        
        # Format a task template
        task_description = "Process user input: {user_input}"
        inputs = {"user_input": "Test input"}
        formatted = bot.format_task_template(task_description, inputs)
        
        # Verify the formatted template
        assert formatted == "Process user input: Test input" 