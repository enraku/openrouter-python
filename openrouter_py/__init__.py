"""OpenRouter Python Library

A Python client library for interacting with OpenRouter AI models.
"""

__version__ = "0.1.0"

from .client.openrouter_client import OpenRouterClient
from .exceptions.errors import APIError, AuthenticationError, OpenRouterError
from .models.balance import Credits, CreditsData
from .models.chat import ChatCompletion, ChatCompletionChoice, ChatMessage

__all__ = [
    "OpenRouterClient",
    "ChatMessage",
    "ChatCompletion",
    "ChatCompletionChoice",
    "Credits",
    "CreditsData",
    "OpenRouterError",
    "APIError",
    "AuthenticationError",
]

