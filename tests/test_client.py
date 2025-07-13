"""Tests for OpenRouter client."""

from unittest.mock import Mock, patch

import pytest

from openrouter_py import OpenRouterClient
from openrouter_py.exceptions import AuthenticationError


def test_client_init_with_api_key():
    """Test client initialization with API key."""
    client = OpenRouterClient(api_key="test-key")
    assert client.api_key == "test-key"


def test_client_init_without_api_key():
    """Test client initialization without API key raises error."""
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(AuthenticationError):
            OpenRouterClient()


def test_client_init_with_env_var():
    """Test client initialization with environment variable."""
    with patch.dict("os.environ", {"OPENROUTER_API_KEY": "env-key"}):
        client = OpenRouterClient()
        assert client.api_key == "env-key"


def test_context_manager():
    """Test client as context manager."""
    with OpenRouterClient(api_key="test-key") as client:
        assert client.api_key == "test-key"


@patch("httpx.Client.request")
def test_simple_completion(mock_request):
    """Test simple completion method."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "test-id",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "test-model",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Hello, world!"
            },
            "finish_reason": "stop"
        }]
    }
    mock_request.return_value = mock_response

    client = OpenRouterClient(api_key="test-key")
    result = client.simple_completion("Hello", model="test-model")

    assert result == "Hello, world!"
    mock_request.assert_called_once()


@patch("httpx.Client.request")
def test_get_balance(mock_request):
    """Test get balance method."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "total_credits": 10.0,
            "total_usage": 3.5
        }
    }
    mock_request.return_value = mock_response

    client = OpenRouterClient(api_key="test-key")
    balance = client.get_balance()

    assert balance.total_purchased == 10.0
    assert balance.total_used == 3.5
    assert balance.balance == 6.5
    assert balance.data.remaining_credits == 6.5
    mock_request.assert_called_once()

