"""Tests for async OpenRouter client."""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from openrouter_py import AsyncOpenRouterClient
from openrouter_py.exceptions import AuthenticationError


@pytest.mark.asyncio
async def test_async_client_init_with_api_key():
    """Test async client initialization with API key."""
    client = AsyncOpenRouterClient(api_key="test-key")
    assert client.api_key == "test-key"
    await client.close()


@pytest.mark.asyncio
async def test_async_client_init_without_api_key():
    """Test async client initialization without API key raises error."""
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(AuthenticationError):
            AsyncOpenRouterClient()


@pytest.mark.asyncio
async def test_async_client_init_with_env_var():
    """Test async client initialization with environment variable."""
    with patch.dict("os.environ", {"OPENROUTER_API_KEY": "env-key"}):
        client = AsyncOpenRouterClient()
        assert client.api_key == "env-key"
        await client.close()


@pytest.mark.asyncio
async def test_async_context_manager():
    """Test async client as context manager."""
    async with AsyncOpenRouterClient(api_key="test-key") as client:
        assert client.api_key == "test-key"


@pytest.mark.asyncio
@patch("httpx.AsyncClient.request")
async def test_async_simple_completion(mock_request):
    """Test async simple completion method."""
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
                "content": "Hello, async world!"
            },
            "finish_reason": "stop"
        }]
    }
    mock_request.return_value = mock_response

    async with AsyncOpenRouterClient(api_key="test-key") as client:
        result = await client.simple_completion("Hello", model="test-model")

    assert result == "Hello, async world!"
    mock_request.assert_called_once()


@pytest.mark.asyncio
@patch("httpx.AsyncClient.request")
async def test_async_get_balance(mock_request):
    """Test async get balance method."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "total_credits": 15.0,
            "total_usage": 5.0
        }
    }
    mock_request.return_value = mock_response

    async with AsyncOpenRouterClient(api_key="test-key") as client:
        balance = await client.get_balance()

    assert balance.total_purchased == 15.0
    assert balance.total_used == 5.0
    assert balance.balance == 10.0
    mock_request.assert_called_once()


@pytest.mark.asyncio
@patch("httpx.AsyncClient.request")
async def test_async_get_models(mock_request):
    """Test async get models method."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [
            {
                "id": "test-model-1",
                "name": "Test Model 1",
                "description": "A test model",
                "context_length": 4096,
                "pricing": {"prompt": "0.001", "completion": "0.002"}
            },
            {
                "id": "test-model-2", 
                "name": "Test Model 2",
                "description": "Another test model",
                "context_length": 8192,
                "pricing": {"prompt": "0.002", "completion": "0.004"}
            }
        ]
    }
    mock_request.return_value = mock_response

    async with AsyncOpenRouterClient(api_key="test-key") as client:
        models = await client.get_models()

    assert len(models.data) == 2
    assert models.data[0].id == "test-model-1"
    assert models.data[1].id == "test-model-2"
    mock_request.assert_called_once()