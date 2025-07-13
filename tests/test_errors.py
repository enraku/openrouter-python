"""Tests for error handling."""

from unittest.mock import Mock, patch

import httpx
import pytest

from openrouter_py import OpenRouterClient
from openrouter_py.exceptions.errors import (
    APIError,
    AuthenticationError,
    OpenRouterError,
    RateLimitError,
    ValidationError,
)


class TestExceptionModels:
    """Test exception class functionality."""

    def test_openrouter_error_basic(self):
        """Test basic OpenRouterError."""
        error = OpenRouterError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.status_code is None

    def test_openrouter_error_with_status(self):
        """Test OpenRouterError with status code."""
        error = OpenRouterError("API failed", status_code=500)
        assert error.message == "API failed"
        assert error.status_code == 500

    def test_api_error_inheritance(self):
        """Test APIError inherits from OpenRouterError."""
        error = APIError("API specific error", status_code=400)
        assert isinstance(error, OpenRouterError)
        assert error.message == "API specific error"
        assert error.status_code == 400

    def test_authentication_error(self):
        """Test AuthenticationError."""
        error = AuthenticationError("Invalid key")
        assert isinstance(error, OpenRouterError)
        assert error.message == "Invalid key"

    def test_rate_limit_error(self):
        """Test RateLimitError."""
        error = RateLimitError("Too many requests")
        assert isinstance(error, OpenRouterError)
        assert error.message == "Too many requests"

    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError("Invalid data")
        assert isinstance(error, OpenRouterError)
        assert error.message == "Invalid data"


class TestClientErrorHandling:
    """Test client error handling."""

    @patch("httpx.Client.request")
    def test_authentication_error_401(self, mock_request):
        """Test 401 authentication error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_request.return_value = mock_response

        with OpenRouterClient(api_key="invalid-key") as client:
            with pytest.raises(AuthenticationError, match="Invalid API key"):
                client.get_balance()

    @patch("httpx.Client.request")
    def test_rate_limit_error_429(self, mock_request):
        """Test 429 rate limit error."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_request.return_value = mock_response

        with OpenRouterClient(api_key="test-key") as client:
            with pytest.raises(RateLimitError, match="Rate limit exceeded"):
                client.get_balance()

    @patch("httpx.Client.request")
    def test_generic_api_error_400(self, mock_request):
        """Test generic 400 API error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_response.json.side_effect = Exception("Not JSON")
        mock_request.return_value = mock_response

        with OpenRouterClient(api_key="test-key") as client:
            with pytest.raises(APIError) as exc_info:
                client.get_balance()
            
            assert exc_info.value.status_code == 400
            assert "Bad request" in str(exc_info.value)

    @patch("httpx.Client.request")
    def test_api_error_with_json_response(self, mock_request):
        """Test API error with JSON error response."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_response.json.return_value = {
            "error": {"message": "Model not found"}
        }
        mock_request.return_value = mock_response

        with OpenRouterClient(api_key="test-key") as client:
            with pytest.raises(APIError) as exc_info:
                client.get_balance()
            
            assert "Model not found" in str(exc_info.value)

    @patch("httpx.Client.request")
    def test_network_error(self, mock_request):
        """Test network/connection error."""
        mock_request.side_effect = httpx.RequestError("Connection failed")

        with OpenRouterClient(api_key="test-key") as client:
            with pytest.raises(OpenRouterError, match="Request failed"):
                client.get_balance()

    @patch("httpx.Client.request")
    def test_invalid_response_data(self, mock_request):
        """Test invalid response data causing ValidationError."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "invalid": "response"  # Missing required fields
        }
        mock_request.return_value = mock_response

        with OpenRouterClient(api_key="test-key") as client:
            with pytest.raises(ValidationError, match="Invalid response data"):
                client.get_balance()

    def test_missing_api_key(self):
        """Test missing API key raises AuthenticationError."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(AuthenticationError, match="API key is required"):
                OpenRouterClient()

    @patch("httpx.Client.request")
    def test_500_server_error(self, mock_request):
        """Test 500 server error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_response.json.side_effect = Exception("Not JSON")
        mock_request.return_value = mock_response

        with OpenRouterClient(api_key="test-key") as client:
            with pytest.raises(APIError) as exc_info:
                client.get_balance()
            
            assert exc_info.value.status_code == 500
            assert "Internal server error" in str(exc_info.value)


class TestStreamingErrorHandling:
    """Test streaming-specific error handling."""

    @patch("httpx.Client.stream")
    def test_streaming_authentication_error(self, mock_stream):
        """Test streaming authentication error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_stream.return_value.__enter__.return_value = mock_response

        with OpenRouterClient(api_key="invalid-key") as client:
            with pytest.raises(AuthenticationError):
                list(client.simple_completion_stream("test"))

    @patch("httpx.Client.stream")
    def test_streaming_network_error(self, mock_stream):
        """Test streaming network error."""
        mock_stream.side_effect = httpx.RequestError("Network error")

        with OpenRouterClient(api_key="test-key") as client:
            with pytest.raises(OpenRouterError, match="Streaming request failed"):
                list(client.simple_completion_stream("test"))