"""Model information classes for OpenRouter API."""

from typing import Any

from pydantic import BaseModel, Field


class ModelData(BaseModel):
    """Information about an available model."""

    id: str = Field(..., description="Model identifier")
    name: str = Field(..., description="Human-readable model name")
    description: str | None = Field(None, description="Model description")
    context_length: int | None = Field(None, description="Maximum context length")
    pricing: dict[str, Any] | None = Field(None, description="Pricing information")
    top_provider: dict[str, Any] | None = Field(
        None, description="Top provider info"
    )


class Model(BaseModel):
    """Response containing model information."""

    data: list[ModelData] = Field(..., description="List of available models")

