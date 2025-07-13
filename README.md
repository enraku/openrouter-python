# OpenRouter Python Library

A Python client library for interacting with OpenRouter AI models.

📖 **[詳しい使用ガイドはこちら](./USAGE_GUIDE.md)** - 他プロジェクトからの使い方

## Installation

```bash
# From PyPI (when published)
pip install openrouter-py

# From GitHub (current)
pip install git+https://github.com/enraku/openrouter-python.git

# Using uv
uv add git+https://github.com/enraku/openrouter-python.git
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
- ✅ Streaming responses
- ✅ Async client support
- ✅ Model listing and analysis
- ✅ Type hints and validation with Pydantic
- ✅ Comprehensive error handling
- ✅ Rate limit management
- ✅ Retry logic with exponential backoff

## Documentation

📚 **[View Full API Documentation](./docs/_build/html/index.html)**

To build and view documentation locally:

```bash
# Quick way - using the helper script
python view_docs.py

# Or manually build
cd docs && make html
# Then open docs/_build/html/index.html in your browser
```

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