# OpenRouter Python Client Examples 🦈

This directory contains comprehensive examples showing how to use the OpenRouter Python client library.

## Setup

First, set your API key:

```bash
export OPENROUTER_API_KEY="your-api-key-here"
```

## Basic Examples

- [basic_usage.py](basic_usage.py) - Simple client usage
- [chat_examples.py](chat_examples.py) - Chat completion examples
- [balance_monitoring.py](balance_monitoring.py) - Credit monitoring
- [model_exploration.py](model_exploration.py) - Exploring available models

## Advanced Examples

- [async_examples.py](async_examples.py) - Async/await usage
- [streaming_examples.py](streaming_examples.py) - Real-time streaming
- [error_handling.py](error_handling.py) - Comprehensive error handling
- [conversation_manager.py](conversation_manager.py) - Multi-turn conversations

## Specialized Use Cases

- [content_generation.py](content_generation.py) - Content creation
- [data_analysis.py](data_analysis.py) - Using AI for data analysis
- [code_assistant.py](code_assistant.py) - Programming assistance

## Running Examples

```bash
# Install the package in development mode
uv sync

# Run any example
uv run python examples/basic_usage.py
```

## Free Models

All examples use free models when possible to minimize costs:

- `google/gemma-3n-e2b-it:free`
- `mistralai/mistral-small-3.2-24b-instruct:free`
- `deepseek/deepseek-r1-0528-qwen3-8b:free`