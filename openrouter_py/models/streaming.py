"""Streaming response models for OpenRouter API."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class StreamChoice(BaseModel):
    """A single choice from a streaming chat completion response."""

    index: int = Field(..., description="The index of this choice")
    delta: dict[str, Any] = Field(..., description="The delta content")
    finish_reason: Optional[str] = Field(
        None, description="The reason the completion finished"
    )


class StreamChunk(BaseModel):
    """A single chunk from a streaming response."""

    id: str = Field(..., description="Unique identifier for the completion")
    object: str = Field(..., description="The object type")
    created: int = Field(..., description="Unix timestamp of creation")
    model: str = Field(..., description="The model used for completion")
    choices: list[StreamChoice] = Field(..., description="List of streaming choices")

    @property
    def content(self) -> str | None:
        """Get the content from the first choice's delta."""
        if self.choices and self.choices[0].delta:
            return self.choices[0].delta.get("content")
        return None

    @property
    def is_finished(self) -> bool:
        """Check if the stream is finished."""
        return any(
            choice.finish_reason is not None for choice in self.choices
        )