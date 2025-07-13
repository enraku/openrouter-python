#!/usr/bin/env python3
"""Chat completion examples using OpenRouter."""

import os
from typing import List

from openrouter_py import OpenRouterClient
from openrouter_py.models.chat import ChatMessage


def single_message_chat():
    """Simple single message chat."""
    print("💬 Single Message Chat")
    
    with OpenRouterClient() as client:
        messages: List[ChatMessage] = [
            ChatMessage(role="user", content="What is the capital of Japan?")
        ]
        
        completion = client.chat_completion(
            messages=messages,
            model="google/gemma-3n-e2b-it:free",
            max_tokens=30
        )
        
        print(f"User: What is the capital of Japan?")
        print(f"Assistant: {completion.content}")
        
        if completion.usage:
            print(f"📊 Tokens used: {completion.usage.total_tokens}")


def multi_turn_conversation():
    """Multi-turn conversation example."""
    print("\n🔄 Multi-turn Conversation")
    
    with OpenRouterClient() as client:
        # Start conversation
        messages: List[ChatMessage] = [
            ChatMessage(role="user", content="Hello! Can you help me with math?")
        ]
        
        completion = client.chat_completion(
            messages=messages,
            model="mistralai/mistral-small-3.2-24b-instruct:free",
            max_tokens=50
        )
        
        print(f"User: Hello! Can you help me with math?")
        print(f"Assistant: {completion.content}")
        
        # Add assistant response to conversation
        if completion.message:
            messages.append(completion.message)
        
        # Continue conversation
        messages.append(ChatMessage(role="user", content="What is 15 + 27?"))
        
        completion2 = client.chat_completion(
            messages=messages,
            model="mistralai/mistral-small-3.2-24b-instruct:free",
            max_tokens=30
        )
        
        print(f"User: What is 15 + 27?")
        print(f"Assistant: {completion2.content}")


def system_message_example():
    """Using system messages to set behavior."""
    print("\n⚙️ System Message Example")
    
    with OpenRouterClient() as client:
        messages: List[ChatMessage] = [
            ChatMessage(
                role="system", 
                content="You are a helpful assistant that responds in a pirate accent."
            ),
            ChatMessage(role="user", content="Tell me about Python programming.")
        ]
        
        completion = client.chat_completion(
            messages=messages,
            model="google/gemma-3n-e2b-it:free",
            max_tokens=80,
            temperature=0.8  # More creative for character
        )
        
        print(f"System: You are a helpful assistant that responds in a pirate accent.")
        print(f"User: Tell me about Python programming.")
        print(f"Assistant: {completion.content}")


def different_models_comparison():
    """Compare responses from different models."""
    print("\n🔀 Model Comparison")
    
    prompt = "Explain artificial intelligence in one sentence."
    models = [
        "google/gemma-3n-e2b-it:free",
        "mistralai/mistral-small-3.2-24b-instruct:free"
    ]
    
    with OpenRouterClient() as client:
        for model in models:
            response = client.simple_completion(
                prompt,
                model=model,
                max_tokens=50,
                temperature=0.3  # Consistent responses
            )
            print(f"\n🤖 {model.split('/')[-1]}:")
            print(f"   {response}")


def temperature_examples():
    """Show effect of different temperature settings."""
    print("\n🌡️ Temperature Effects")
    
    prompt = "Write a creative opening line for a story about a robot."
    temperatures = [0.1, 0.7, 1.2]
    
    with OpenRouterClient() as client:
        for temp in temperatures:
            response = client.simple_completion(
                prompt,
                model="google/gemma-3n-e2b-it:free",
                max_tokens=30,
                temperature=temp
            )
            print(f"\nTemperature {temp}: {response}")


def main():
    """Run all chat examples."""
    print("🦈 OpenRouter Chat Examples")
    
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ Please set OPENROUTER_API_KEY environment variable")
        return
    
    single_message_chat()
    multi_turn_conversation()
    system_message_example()
    different_models_comparison()
    temperature_examples()
    
    print("\n✅ All chat examples completed!")


if __name__ == "__main__":
    main()