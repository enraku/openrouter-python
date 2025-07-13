"""OpenRouter API client."""

import os
from collections.abc import Sequence
from typing import Any

import httpx
from pydantic import ValidationError

from ..exceptions.errors import (
    APIError,
    AuthenticationError,
    OpenRouterError,
    RateLimitError,
)
from ..exceptions.errors import (
    ValidationError as ValidationErr,
)
from ..models.balance import Credits
from ..models.chat import ChatCompletion, ChatMessage
from ..models.model import Model


class OpenRouterClient:
    """Client for interacting with the OpenRouter API."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://openrouter.ai/api/v1",
        timeout: float = 30.0,
    ) -> None:
        """Initialize the OpenRouter client.

        Args:
            api_key: OpenRouter API key. If not provided, will look for
                OPENROUTER_API_KEY env var.
            base_url: Base URL for the OpenRouter API.
            timeout: Request timeout in seconds.
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key is required. Set OPENROUTER_API_KEY env var or pass "
                "api_key parameter."
            )

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self._client = httpx.Client(
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

    def __enter__(self) -> "OpenRouterClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a request to the OpenRouter API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            json_data: JSON data to send with the request

        Returns:
            Response data as dictionary

        Raises:
            OpenRouterError: For various API errors
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = self._client.request(method, url, json=json_data)

            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code >= 400:
                error_detail = response.text
                try:
                    error_data = response.json()
                    error_detail = error_data.get("error", {}).get(
                        "message", error_detail
                    )
                except Exception:
                    pass
                raise APIError(
                    f"API error: {error_detail}", status_code=response.status_code
                )

            return response.json()  # type: ignore[no-any-return]

        except httpx.RequestError as e:
            raise OpenRouterError(f"Request failed: {str(e)}")

    def chat_completion(
        self,
        messages: Sequence[ChatMessage | dict[str, Any]],
        model: str,
        max_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> ChatCompletion:
        """Create a chat completion.

        Args:
            messages: List of messages in the conversation
            model: The model to use for completion
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0-2)
            top_p: Nucleus sampling parameter (0-1)
            stream: Whether to stream the response
            **kwargs: Additional parameters

        Returns:
            ChatCompletion object with the response

        Raises:
            ValidationError: If the request data is invalid
            OpenRouterError: For API errors
        """
        # Convert ChatMessage objects to dictionaries
        messages_data = []
        for msg in messages:
            if isinstance(msg, ChatMessage):
                messages_data.append(msg.model_dump(exclude_none=True))
            else:
                messages_data.append(msg)

        data = {
            "model": model,
            "messages": messages_data,
            **kwargs,
        }

        if max_tokens is not None:
            data["max_tokens"] = max_tokens
        if temperature is not None:
            data["temperature"] = temperature
        if top_p is not None:
            data["top_p"] = top_p
        if stream:
            data["stream"] = stream

        try:
            response_data = self._make_request("POST", "/chat/completions", data)
            return ChatCompletion(**response_data)
        except ValidationError as e:
            raise ValidationErr(f"Invalid response data: {str(e)}")

    def get_models(self) -> Model:
        """Get available models.

        Returns:
            Model object containing list of available models

        Raises:
            OpenRouterError: For API errors
        """
        try:
            response_data = self._make_request("GET", "/models")
            return Model(**response_data)
        except ValidationError as e:
            raise ValidationErr(f"Invalid response data: {str(e)}")

    def get_balance(self) -> Credits:
        """Get account balance and credits information.

        Returns:
            Credits object containing balance and usage information

        Raises:
            OpenRouterError: For API errors
        """
        try:
            response_data = self._make_request("GET", "/credits")
            return Credits(**response_data)
        except ValidationError as e:
            raise ValidationErr(f"Invalid response data: {str(e)}")

    def simple_completion(
        self,
        prompt: str,
        model: str = "anthropic/claude-3.5-sonnet",
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        """Simple text completion method for convenience.

        Args:
            prompt: The text prompt
            model: The model to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            The completion text
        """
        messages = [ChatMessage(role="user", content=prompt)]
        completion = self.chat_completion(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return completion.content or ""

