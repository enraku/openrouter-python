"""Balance and credits models for OpenRouter API."""

from pydantic import BaseModel, Field


class CreditsData(BaseModel):
    """Credits information for a user account."""

    total_credits: float = Field(..., description="Total credits purchased")
    total_usage: float = Field(..., description="Total credits used")

    @property
    def remaining_credits(self) -> float:
        """Calculate remaining credits."""
        return self.total_credits - self.total_usage


class Credits(BaseModel):
    """Response from the credits API."""

    data: CreditsData = Field(..., description="Credits information")

    @property
    def balance(self) -> float:
        """Get remaining balance for convenience."""
        return self.data.remaining_credits

    @property
    def total_purchased(self) -> float:
        """Get total credits purchased for convenience."""
        return self.data.total_credits

    @property
    def total_used(self) -> float:
        """Get total credits used for convenience."""
        return self.data.total_usage
