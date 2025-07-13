"""Exception classes for OpenRouter library."""

from .errors import APIError, AuthenticationError, OpenRouterError, RateLimitError

__all__ = ["OpenRouterError", "APIError", "AuthenticationError", "RateLimitError"]

