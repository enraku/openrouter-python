"""Async OpenRouter API client."""

import json
import os
from collections.abc import AsyncIterator, Sequence
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
from ..models.streaming import StreamChunk


class AsyncOpenRouterClient:
    """Async client for interacting with the OpenRouter API."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://openrouter.ai/api/v1",
        timeout: float = 30.0,
    ) -> None:
        """Initialize the async OpenRouter client.

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

        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

    async def __aenter__(self) -> "AsyncOpenRouterClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the async HTTP client."""
        await self._client.aclose()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an async request to the OpenRouter API.

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
            response = await self._client.request(method, url, json=json_data)

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

    async def chat_completion(
        self,
        messages: Sequence[ChatMessage | dict[str, Any]],
        model: str,
        max_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> ChatCompletion:
        """Create an async chat completion.

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
            response_data = await self._make_request("POST", "/chat/completions", data)
            return ChatCompletion(**response_data)
        except ValidationError as e:
            raise ValidationErr(f"Invalid response data: {str(e)}")

    async def get_models(self) -> Model:
        """Get available models asynchronously.

        Returns:
            Model object containing list of available models

        Raises:
            OpenRouterError: For API errors
        """
        try:
            response_data = await self._make_request("GET", "/models")
            return Model(**response_data)
        except ValidationError as e:
            raise ValidationErr(f"Invalid response data: {str(e)}")

    async def get_balance(self) -> Credits:
        """Get account balance and credits information asynchronously.

        Returns:
            Credits object containing balance and usage information

        Raises:
            OpenRouterError: For API errors
        """
        try:
            response_data = await self._make_request("GET", "/credits")
            return Credits(**response_data)
        except ValidationError as e:
            raise ValidationErr(f"Invalid response data: {str(e)}")

    async def simple_completion(
        self,
        prompt: str,
        model: str = "anthropic/claude-3.5-sonnet",
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        """Simple async text completion method for convenience.

        Args:
            prompt: The text prompt
            model: The model to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            The completion text
        """
        messages = [ChatMessage(role="user", content=prompt)]
        completion = await self.chat_completion(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return completion.content or ""

    async def chat_completion_stream(
        self,
        messages: Sequence[ChatMessage | dict[str, Any]],
        model: str,
        max_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[StreamChunk]:
        """Create an async streaming chat completion.

        Args:
            messages: List of messages in the conversation
            model: The model to use for completion
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0-2)
            top_p: Nucleus sampling parameter (0-1)
            **kwargs: Additional parameters

        Yields:
            StreamChunk objects with incremental response data

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
            "stream": True,
            **kwargs,
        }

        if max_tokens is not None:
            data["max_tokens"] = max_tokens
        if temperature is not None:
            data["temperature"] = temperature
        if top_p is not None:
            data["top_p"] = top_p

        url = f"{self.base_url}/chat/completions"

        try:
            async with self._client.stream("POST", url, json=data) as response:
                if response.status_code == 401:
                    raise AuthenticationError("Invalid API key")
                elif response.status_code == 429:
                    raise RateLimitError("Rate limit exceeded")
                elif response.status_code >= 400:
                    error_detail = await response.aread()
                    raise APIError(
                        f"API error: {error_detail.decode()}", 
                        status_code=response.status_code
                    )

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: " prefix
                        
                        if data_str.strip() == "[DONE]":
                            break
                            
                        try:
                            chunk_data = json.loads(data_str)
                            yield StreamChunk(**chunk_data)
                        except (json.JSONDecodeError, ValidationError) as e:
                            # Skip invalid chunks
                            continue

        except httpx.RequestError as e:
            raise OpenRouterError(f"Async streaming request failed: {str(e)}")

    async def simple_completion_stream(
        self,
        prompt: str,
        model: str = "anthropic/claude-3.5-sonnet",
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> AsyncIterator[str]:
        """Simple async streaming text completion method for convenience.

        Args:
            prompt: The text prompt
            model: The model to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Yields:
            Content strings from the streaming response
        """
        messages = [ChatMessage(role="user", content=prompt)]
        
        async for chunk in self.chat_completion_stream(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        ):
            if chunk.content:
                yield chunk.content