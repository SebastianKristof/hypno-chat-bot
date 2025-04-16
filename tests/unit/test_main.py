import os
import sys
import pytest
from unittest.mock import patch, MagicMock, call
from io import StringIO
from pathlib import Path

# Add the project root to the system path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

class TestMain:
    """Tests for the main module."""
    
    @patch('builtins.input')
    @patch('builtins.print')
    @patch('src.hypnobot.main.HypnoBot')
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    def test_main_function(self, mock_hypnobot, mock_print, mock_input):
        """Test the main function."""
        # Mock the HypnoBot class
        mock_bot_instance = MagicMock()
        mock_bot_instance.process_input.return_value = "Test response"
        mock_hypnobot.return_value = mock_bot_instance
        
        # Mock the input function to return "exit" after "Test input"
        mock_input.side_effect = ["Test input", "exit"]
        
        # Import the main module after mocking environment
        from src.hypnobot.main import main
        
        # Run the main function
        main()
        
        # Verify the calls
        assert mock_hypnobot.called
        mock_bot_instance.process_input.assert_called_once_with("Test input")
        
        # Verify the print statements (partial check)
        expected_calls = [
            call("HypnoBot v2 - Hypnotherapy Chatbot"),
            call("Type 'exit' to quit the chat"),
            call("-" * 50),
        ]
        mock_print.assert_has_calls(expected_calls, any_order=False)
    
    @patch('builtins.print')
    @patch.dict(os.environ, {}, clear=True)
    def test_main_function_no_api_key(self, mock_print):
        """Test the main function without an API key."""
        # Import the main module after clearing environment
        from src.hypnobot.main import main
        
        # Run the main function
        main()
        
        # Verify the print statements
        expected_calls = [
            call("Error: OPENAI_API_KEY not found in environment variables."),
            call("Please set your OpenAI API key before running the bot."),
            call("You can create a .env file based on .env.example")
        ]
        mock_print.assert_has_calls(expected_calls, any_order=False)
    
    @patch('builtins.input')
    @patch('builtins.print')
    @patch('src.hypnobot.main.HypnoBot')
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    def test_main_function_error(self, mock_hypnobot, mock_print, mock_input):
        """Test the main function with an error in process_input."""
        # Mock the HypnoBot class
        mock_bot_instance = MagicMock()
        mock_bot_instance.process_input.side_effect = Exception("Test error")
        mock_hypnobot.return_value = mock_bot_instance
        
        # Mock the input function to return "exit" after "Test input"
        mock_input.side_effect = ["Test input", "exit"]
        
        # Import the main module after mocking environment
        from src.hypnobot.main import main
        
        # Run the main function
        main()
        
        # Verify the calls
        assert mock_hypnobot.called
        mock_bot_instance.process_input.assert_called_once_with("Test input")
        
        # Verify the error handling print statements
        error_calls = [
            call("\nError: Test error"),
            call("HypnoBot: I'm sorry, I encountered an error processing your request.")
        ]
        mock_print.assert_has_calls(error_calls, any_order=False) 