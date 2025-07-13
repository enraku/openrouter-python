"""Tests for streaming functionality."""

import json
from unittest.mock import Mock, patch

import pytest

from openrouter_py import OpenRouterClient
from openrouter_py.models.streaming import StreamChunk, StreamChoice


def test_stream_chunk_model():
    """Test StreamChunk model."""
    chunk_data = {
        "id": "test-stream-id",
        "object": "chat.completion.chunk",
        "created": 1234567890,
        "model": "test-model",
        "choices": [{
            "index": 0,
            "delta": {"content": "Hello"},
            "finish_reason": None
        }]
    }
    
    chunk = StreamChunk(**chunk_data)
    assert chunk.id == "test-stream-id"
    assert chunk.content == "Hello"
    assert not chunk.is_finished


def test_stream_chunk_finished():
    """Test StreamChunk finished state."""
    chunk_data = {
        "id": "test-stream-id",
        "object": "chat.completion.chunk", 
        "created": 1234567890,
        "model": "test-model",
        "choices": [{
            "index": 0,
            "delta": {},
            "finish_reason": "stop"
        }]
    }
    
    chunk = StreamChunk(**chunk_data)
    assert chunk.content is None
    assert chunk.is_finished


def test_stream_choice_model():
    """Test StreamChoice model."""
    choice_data = {
        "index": 0,
        "delta": {"content": "Test content", "role": "assistant"},
        "finish_reason": None
    }
    
    choice = StreamChoice(**choice_data)
    assert choice.index == 0
    assert choice.delta["content"] == "Test content"
    assert choice.finish_reason is None


@patch("httpx.Client.stream")
def test_sync_streaming(mock_stream):
    """Test synchronous streaming."""
    # Mock the streaming response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.iter_lines.return_value = [
        "data: " + json.dumps({
            "id": "test-id",
            "object": "chat.completion.chunk",
            "created": 1234567890,
            "model": "test-model",
            "choices": [{
                "index": 0,
                "delta": {"content": "Hello"},
                "finish_reason": None
            }]
        }),
        "data: " + json.dumps({
            "id": "test-id",
            "object": "chat.completion.chunk",
            "created": 1234567890,
            "model": "test-model", 
            "choices": [{
                "index": 0,
                "delta": {"content": " world!"},
                "finish_reason": None
            }]
        }),
        "data: " + json.dumps({
            "id": "test-id",
            "object": "chat.completion.chunk",
            "created": 1234567890,
            "model": "test-model",
            "choices": [{
                "index": 0,
                "delta": {},
                "finish_reason": "stop"
            }]
        }),
        "data: [DONE]"
    ]
    
    mock_stream.return_value.__enter__.return_value = mock_response
    
    with OpenRouterClient(api_key="test-key") as client:
        chunks = list(client.simple_completion_stream("Test prompt", model="test-model"))
    
    assert len(chunks) == 2  # Only chunks with content
    assert chunks[0] == "Hello"
    assert chunks[1] == " world!"


@patch("httpx.Client.stream")
def test_sync_chat_streaming(mock_stream):
    """Test synchronous chat streaming."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.iter_lines.return_value = [
        "data: " + json.dumps({
            "id": "test-id",
            "object": "chat.completion.chunk",
            "created": 1234567890,
            "model": "test-model",
            "choices": [{
                "index": 0,
                "delta": {"content": "Test"},
                "finish_reason": None
            }]
        }),
        "data: [DONE]"
    ]
    
    mock_stream.return_value.__enter__.return_value = mock_response
    
    with OpenRouterClient(api_key="test-key") as client:
        chunks = list(client.chat_completion_stream(
            messages=[{"role": "user", "content": "Test"}],
            model="test-model"
        ))
    
    assert len(chunks) == 1
    assert chunks[0].content == "Test"
    assert not chunks[0].is_finished


def test_invalid_stream_data():
    """Test handling of invalid stream data."""
    chunk_data = {
        "id": "test-id",
        "object": "chat.completion.chunk",
        "created": 1234567890,
        "model": "test-model", 
        "choices": []  # Empty choices
    }
    
    chunk = StreamChunk(**chunk_data)
    assert chunk.content is None
    assert not chunk.is_finished