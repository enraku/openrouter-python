"""Exception classes for the OpenRouter client."""



class OpenRouterError(Exception):
    """Base exception class for OpenRouter library."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class APIError(OpenRouterError):
    """Raised when the API returns an error response."""
    pass


class AuthenticationError(OpenRouterError):
    """Raised when API key is invalid or missing."""
    pass


class RateLimitError(OpenRouterError):
    """Raised when API rate limit is exceeded."""
    pass


class ValidationError(OpenRouterError):
    """Raised when request validation fails."""
    pass

