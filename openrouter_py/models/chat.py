"""Chat completion models for OpenRouter API."""

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A message in a chat conversation."""

    role: str = Field(..., description="The role of the message author")
    content: str = Field(..., description="The content of the message")
    name: str | None = Field(None, description="The name of the author")


class ChatCompletionUsage(BaseModel):
    """Token usage information for a chat completion."""

    prompt_tokens: int = Field(..., description="Number of tokens in the prompt")
    completion_tokens: int = Field(
        ..., description="Number of tokens in the completion"
    )
    total_tokens: int = Field(..., description="Total number of tokens used")


class ChatCompletionChoice(BaseModel):
    """A single choice from a chat completion response."""

    index: int = Field(..., description="The index of this choice")
    message: ChatMessage = Field(..., description="The message content")
    finish_reason: str | None = Field(
        None, description="The reason the completion finished"
    )


class ChatCompletion(BaseModel):
    """Response from the chat completions API."""

    id: str = Field(..., description="Unique identifier for the chat completion")
    object: str = Field(..., description="The object type")
    created: int = Field(..., description="Unix timestamp of creation")
    model: str = Field(..., description="The model used for completion")
    choices: list[ChatCompletionChoice] = Field(
        ..., description="List of completion choices"
    )
    usage: ChatCompletionUsage | None = Field(None, description="Usage statistics")

    @property
    def message(self) -> ChatMessage | None:
        """Get the first choice's message for convenience."""
        return self.choices[0].message if self.choices else None

    @property
    def content(self) -> str | None:
        """Get the first choice's message content for convenience."""
        return self.message.content if self.message else None

