#!/usr/bin/env python3
"""Async usage examples for OpenRouter Python client."""

import asyncio
import os
import time
from typing import List

from openrouter_py import AsyncOpenRouterClient
from openrouter_py.models.chat import ChatMessage


async def basic_async_usage():
    """Basic async client usage."""
    print("🚀 Basic Async Usage")
    
    async with AsyncOpenRouterClient() as client:
        # Simple async completion
        response = await client.simple_completion(
            "What is async programming?",
            model="google/gemma-3n-e2b-it:free",
            max_tokens=50
        )
        print(f"Response: {response}")
        
        # Check balance asynchronously
        balance = await client.get_balance()
        print(f"💰 Balance: ${balance.balance:.4f}")


async def concurrent_requests():
    """Demonstrate concurrent API requests."""
    print("\n⚡ Concurrent Requests")
    
    async with AsyncOpenRouterClient() as client:
        # Define multiple prompts
        prompts = [
            "Name a color",
            "Name an animal", 
            "Name a country",
            "Name a programming language",
            "Name a planet"
        ]
        
        print("🚀 Starting 5 concurrent requests...")
        start_time = time.time()
        
        # Execute all requests concurrently
        tasks = [
            client.simple_completion(
                prompt,
                model="google/gemma-3n-e2b-it:free",
                max_tokens=10
            )
            for prompt in prompts
        ]
        
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        print(f"⏱️ Completed in {end_time - start_time:.2f} seconds")
        print("\n📋 Results:")
        for prompt, result in zip(prompts, results):
            print(f"   {prompt}: {result.strip()}")


async def async_conversation():
    """Async multi-turn conversation."""
    print("\n💬 Async Conversation")
    
    async with AsyncOpenRouterClient() as client:
        messages: List[ChatMessage] = [
            ChatMessage(role="user", content="Hi! What's your favorite programming concept?")
        ]
        
        completion = await client.chat_completion(
            messages=messages,
            model="mistralai/mistral-small-3.2-24b-instruct:free",
            max_tokens=60
        )
        
        print(f"User: Hi! What's your favorite programming concept?")
        print(f"Assistant: {completion.content}")
        
        # Continue conversation
        if completion.message:
            messages.append(completion.message)
        
        messages.append(ChatMessage(
            role="user", 
            content="Can you give me a simple example?"
        ))
        
        completion2 = await client.chat_completion(
            messages=messages,
            model="mistralai/mistral-small-3.2-24b-instruct:free",
            max_tokens=80
        )
        
        print(f"User: Can you give me a simple example?")
        print(f"Assistant: {completion2.content}")


async def rate_limited_requests():
    """Handle rate limiting with async."""
    print("\n🛡️ Rate-Limited Sequential Requests")
    
    async with AsyncOpenRouterClient() as client:
        questions = [
            "What is 1+1?",
            "What is 2+2?", 
            "What is 3+3?",
            "What is 4+4?",
            "What is 5+5?"
        ]
        
        print("⏳ Making sequential requests with delays...")
        
        for i, question in enumerate(questions, 1):
            response = await client.simple_completion(
                question,
                model="google/gemma-3n-e2b-it:free",
                max_tokens=10
            )
            print(f"   {i}. {question} → {response.strip()}")
            
            # Small delay to be respectful to the API
            if i < len(questions):
                await asyncio.sleep(0.5)


async def async_with_error_handling():
    """Async usage with error handling."""
    print("\n🛡️ Async Error Handling")
    
    try:
        async with AsyncOpenRouterClient() as client:
            # This might fail if model doesn't exist
            response = await client.simple_completion(
                "Test prompt",
                model="nonexistent/model:free",
                max_tokens=10
            )
            print(f"Response: {response}")
            
    except Exception as e:
        print(f"⚠️  Caught error: {e}")
        print("✅ Error handling working correctly!")


async def async_model_exploration():
    """Explore models asynchronously."""
    print("\n🔍 Async Model Exploration")
    
    async with AsyncOpenRouterClient() as client:
        print("🔍 Fetching available models...")
        models = await client.get_models()
        
        # Find free models
        free_models = [m for m in models.data if ":free" in m.id]
        print(f"🆓 Found {len(free_models)} free models")
        
        # Test a few models concurrently
        test_models = free_models[:3]  # Test first 3
        prompt = "Say hello"
        
        print(f"🧪 Testing {len(test_models)} models concurrently...")
        
        tasks = [
            client.simple_completion(prompt, model=model.id, max_tokens=10)
            for model in test_models
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for model, result in zip(test_models, results):
            if isinstance(result, Exception):
                print(f"   ❌ {model.id}: {result}")
            else:
                print(f"   ✅ {model.id}: {result.strip()}")


async def main():
    """Run all async examples."""
    print("🦈 OpenRouter Async Examples")
    
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ Please set OPENROUTER_API_KEY environment variable")
        return
    
    await basic_async_usage()
    await concurrent_requests()
    await async_conversation()
    await rate_limited_requests()
    await async_with_error_handling()
    await async_model_exploration()
    
    print("\n✅ All async examples completed!")


if __name__ == "__main__":
    asyncio.run(main())