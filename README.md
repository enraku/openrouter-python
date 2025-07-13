# OpenRouter Python Library

A Python client library for interacting with OpenRouter AI models.

## Installation

```bash
pip install openrouter-py
```

## Quick Start

```python
from openrouter_py import OpenRouterClient, ChatMessage

# Initialize client with API key
client = OpenRouterClient(api_key="your-api-key")

# Or use environment variable OPENROUTER_API_KEY
client = OpenRouterClient()

# Simple completion
response = client.simple_completion(
    "What is the capital of Japan?",
    model="anthropic/claude-3.5-sonnet"
)
print(response)

# Chat completion
messages = [
    ChatMessage(role="user", content="Hello! How are you?")
]

completion = client.chat_completion(
    messages=messages,
    model="anthropic/claude-3.5-sonnet",
    max_tokens=100
)

print(completion.content)
```

## Features

- ✅ Chat completions
- ✅ Model listing
- ✅ Type hints and validation with Pydantic
- ✅ Error handling
- ✅ Async support (coming soon)

## Development

This project uses `uv` for dependency management:

```bash
# Install dependencies
uv sync --dev

# Run tests
uv run pytest

# Run linting
uv run ruff check

# Format code
uv run ruff format
```

## License

MIT