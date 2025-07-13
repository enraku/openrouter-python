"""Tests for data models."""

import pytest
from pydantic import ValidationError

from openrouter_py.models.balance import Credits, CreditsData
from openrouter_py.models.chat import (
    ChatCompletion,
    ChatCompletionChoice,
    ChatCompletionUsage,
    ChatMessage,
)
from openrouter_py.models.model import Model, ModelData


class TestChatModels:
    """Test chat-related models."""

    def test_chat_message_valid(self):
        """Test valid ChatMessage creation."""
        message = ChatMessage(role="user", content="Hello")
        assert message.role == "user"
        assert message.content == "Hello"
        assert message.name is None

    def test_chat_message_with_name(self):
        """Test ChatMessage with name."""
        message = ChatMessage(role="assistant", content="Hi", name="bot")
        assert message.role == "assistant"
        assert message.content == "Hi"
        assert message.name == "bot"

    def test_chat_completion_usage(self):
        """Test ChatCompletionUsage model."""
        usage = ChatCompletionUsage(
            prompt_tokens=10,
            completion_tokens=15,
            total_tokens=25
        )
        assert usage.prompt_tokens == 10
        assert usage.completion_tokens == 15
        assert usage.total_tokens == 25

    def test_chat_completion_choice(self):
        """Test ChatCompletionChoice model."""
        message = ChatMessage(role="assistant", content="Response")
        choice = ChatCompletionChoice(
            index=0,
            message=message,
            finish_reason="stop"
        )
        assert choice.index == 0
        assert choice.message == message
        assert choice.finish_reason == "stop"

    def test_chat_completion_full(self):
        """Test full ChatCompletion model."""
        message = ChatMessage(role="assistant", content="Test response")
        choice = ChatCompletionChoice(index=0, message=message)
        usage = ChatCompletionUsage(prompt_tokens=5, completion_tokens=10, total_tokens=15)
        
        completion = ChatCompletion(
            id="test-id",
            object="chat.completion",
            created=1234567890,
            model="test-model",
            choices=[choice],
            usage=usage
        )
        
        assert completion.id == "test-id"
        assert completion.message == message
        assert completion.content == "Test response"
        assert completion.usage == usage


class TestBalanceModels:
    """Test balance-related models."""

    def test_credits_data(self):
        """Test CreditsData model."""
        data = CreditsData(total_credits=100.0, total_usage=25.0)
        assert data.total_credits == 100.0
        assert data.total_usage == 25.0
        assert data.remaining_credits == 75.0

    def test_credits_data_zero_usage(self):
        """Test CreditsData with zero usage."""
        data = CreditsData(total_credits=50.0, total_usage=0.0)
        assert data.remaining_credits == 50.0

    def test_credits_model(self):
        """Test Credits model."""
        data = CreditsData(total_credits=200.0, total_usage=50.0)
        credits = Credits(data=data)
        
        assert credits.balance == 150.0
        assert credits.total_purchased == 200.0
        assert credits.total_used == 50.0

    def test_credits_negative_remaining(self):
        """Test Credits with negative remaining balance."""
        data = CreditsData(total_credits=10.0, total_usage=15.0)
        credits = Credits(data=data)
        assert credits.balance == -5.0


class TestModelModels:
    """Test model-related models."""

    def test_model_data_minimal(self):
        """Test ModelData with minimal fields."""
        model = ModelData(id="test-model", name="Test Model")
        assert model.id == "test-model"
        assert model.name == "Test Model"
        assert model.description is None
        assert model.context_length is None
        assert model.pricing is None

    def test_model_data_full(self):
        """Test ModelData with all fields."""
        model = ModelData(
            id="gpt-4",
            name="GPT-4",
            description="Large language model",
            context_length=8192,
            pricing={"prompt": "0.03", "completion": "0.06"},
            top_provider={"name": "OpenAI", "max_completion_tokens": 4096}
        )
        
        assert model.id == "gpt-4"
        assert model.name == "GPT-4"
        assert model.description == "Large language model"
        assert model.context_length == 8192
        assert model.pricing["prompt"] == "0.03"

    def test_model_list(self):
        """Test Model with list of ModelData."""
        model_data = [
            ModelData(id="model-1", name="Model 1"),
            ModelData(id="model-2", name="Model 2")
        ]
        model_list = Model(data=model_data)
        
        assert len(model_list.data) == 2
        assert model_list.data[0].id == "model-1"
        assert model_list.data[1].id == "model-2"


class TestModelValidation:
    """Test model validation errors."""

    def test_chat_message_missing_required(self):
        """Test ChatMessage with missing required fields."""
        with pytest.raises(ValidationError):
            ChatMessage(role="user")  # Missing content

    def test_credits_data_invalid_type(self):
        """Test CreditsData with invalid types."""
        with pytest.raises(ValidationError):
            CreditsData(total_credits="invalid", total_usage=10.0)

    def test_model_data_empty_id(self):
        """Test ModelData with empty ID."""
        # Empty string is actually valid, but None should raise error
        with pytest.raises(ValidationError):
            ModelData(id=None, name="Test")  # type: ignore