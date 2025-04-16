import os
import sys
import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add the project root to the system path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

# Import the app with patched environment
with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
    from src.hypnobot.api import app

# Create a test client
client = TestClient(app)

class TestHypnoBotAPI:
    """Integration tests for the HypnoBot API."""
    
    @patch('src.hypnobot.api.HypnoBot')
    def test_health_check(self, mock_hypnobot):
        """Test the health check endpoint."""
        # Send a request to the health check endpoint
        response = client.get("/api/health")
        
        # Verify the response
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    @patch('src.hypnobot.api.HypnoBot')
    def test_chat_endpoint(self, mock_hypnobot):
        """Test the chat endpoint."""
        # Mock the HypnoBot class
        mock_bot_instance = MagicMock()
        mock_bot_instance.process_input.return_value = "Test response"
        mock_hypnobot.return_value = mock_bot_instance
        
        # Set the global bot instance directly
        from src.hypnobot.api import bot
        import src.hypnobot.api as api
        api.bot = mock_bot_instance  # Set bot directly

        # Send a request to the chat endpoint
        response = client.post(
            "/api/chat",
            json={"user_input": "Test input"}
        )
        
        # Verify the response
        assert response.status_code == 200
        assert response.json() == {"response": "Test response"}
        mock_bot_instance.process_input.assert_called_once_with("Test input")
    
    @patch('src.hypnobot.api.HypnoBot')
    def test_chat_endpoint_error(self, mock_hypnobot):
        """Test the chat endpoint with an error."""
        # Mock the HypnoBot class
        mock_bot_instance = MagicMock()
        mock_bot_instance.process_input.side_effect = Exception("Test error")
        mock_hypnobot.return_value = mock_bot_instance
        
        # Set the global bot instance directly
        from src.hypnobot.api import bot
        import src.hypnobot.api as api
        api.bot = mock_bot_instance  # Set bot directly
        
        # Send a request to the chat endpoint
        response = client.post(
            "/api/chat",
            json={"user_input": "Test input"}
        )
        
        # Verify the response
        assert response.status_code == 500
        assert response.json() == {"detail": "Test error"} 