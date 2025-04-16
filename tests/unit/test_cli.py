import os
import sys
import pytest
from unittest.mock import patch, MagicMock, call
from pathlib import Path

# Add the project root to the system path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

import run_cli

class TestCLI:
    """Tests for the CLI script."""
    
    @patch('run_cli.HypnoBot')
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    def test_main_single_message(self, mock_hypnobot):
        """Test the main function with a single message."""
        # Mock the HypnoBot class
        mock_bot_instance = MagicMock()
        mock_bot_instance.process_input.return_value = "Test response"
        mock_bot_instance.model_name = "gpt-3.5-turbo"
        mock_hypnobot.return_value = mock_bot_instance
        
        # Set up the command-line arguments
        test_args = ["run_cli.py", "--single", "Test input"]
        with patch('sys.argv', test_args):
            # Run the main function
            exit_code = run_cli.main()
            
            # Verify the exit code and calls
            assert exit_code == 0
            mock_hypnobot.assert_called_once_with(model_name=None)
            mock_bot_instance.process_input.assert_called_once_with("Test input")
    
    @patch('run_cli.HypnoBot')
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    def test_main_with_model(self, mock_hypnobot):
        """Test the main function with a specific model."""
        # Mock the HypnoBot class
        mock_bot_instance = MagicMock()
        mock_bot_instance.model_name = "gpt-4"
        mock_hypnobot.return_value = mock_bot_instance
        
        # Set up the command-line arguments
        test_args = ["run_cli.py", "--model", "gpt-4", "--single", "Test input"]
        with patch('sys.argv', test_args):
            # Run the main function
            run_cli.main()
            
            # Verify the calls
            mock_hypnobot.assert_called_once_with(model_name="gpt-4")
    
    @patch('builtins.input')
    @patch('run_cli.HypnoBot')
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    def test_main_interactive(self, mock_hypnobot, mock_input):
        """Test the main function in interactive mode."""
        # Mock the HypnoBot class
        mock_bot_instance = MagicMock()
        mock_bot_instance.process_input.return_value = "Test response"
        mock_hypnobot.return_value = mock_bot_instance
        
        # Mock the input function to return "exit" after "Test input"
        mock_input.side_effect = ["Test input", "exit"]
        
        # Set up the command-line arguments
        test_args = ["run_cli.py"]
        with patch('sys.argv', test_args):
            # Run the main function
            exit_code = run_cli.main()
            
            # Verify the exit code and calls
            assert exit_code == 0
            mock_hypnobot.assert_called_once_with(model_name=None)
            mock_bot_instance.process_input.assert_called_once_with("Test input")
    
    @patch.dict(os.environ, {}, clear=True)
    def test_main_no_api_key(self):
        """Test the main function without an API key."""
        # Set up the command-line arguments
        test_args = ["run_cli.py"]
        with patch('sys.argv', test_args):
            # Run the main function
            exit_code = run_cli.main()
            
            # Verify the exit code
            assert exit_code == 1 