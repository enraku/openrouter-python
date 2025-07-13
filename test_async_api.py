#!/usr/bin/env python3
"""Test async OpenRouter API client."""

import asyncio
import os
from typing import List

from openrouter_py import AsyncOpenRouterClient
from openrouter_py.models.chat import ChatMessage


async def test_async_api():
    """Test async client with real OpenRouter API."""
    print("🦈 Async OpenRouter API Test Starting...")
    
    # Check API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY environment variable not set")
        return False
    
    try:
        async with AsyncOpenRouterClient() as client:
            
            # Test 1: Get Balance (async)
            print("\n1️⃣ Testing async get_balance()...")
            balance = await client.get_balance()
            print(f"   💰 Balance: ${balance.balance:.4f}")
            
            # Test 2: Get Models (async) 
            print("\n2️⃣ Testing async get_models()...")
            models = await client.get_models()
            print(f"   📋 Found {len(models.data)} models")
            
            # Test 3: Simple Completion (async)
            print("\n3️⃣ Testing async simple_completion()...")
            response = await client.simple_completion(
                "Count from 1 to 3 in English.",
                model="google/gemma-3n-e2b-it:free",
                max_tokens=30
            )
            print(f"   🗣️ Response: {response}")
            
            # Test 4: Chat Completion with messages (async)
            print("\n4️⃣ Testing async chat_completion()...")
            messages: List[ChatMessage] = [
                ChatMessage(role="user", content="What is the capital of Japan? One word answer.")
            ]
            completion = await client.chat_completion(
                messages=messages,
                model="mistralai/mistral-small-3.2-24b-instruct:free",
                max_tokens=10,
                temperature=0.1
            )
            print(f"   💬 Chat response: {completion.content}")
            
            # Test 5: Concurrent requests
            print("\n5️⃣ Testing concurrent async requests...")
            tasks = [
                client.simple_completion("Say 'A'", model="google/gemma-3n-e2b-it:free", max_tokens=5),
                client.simple_completion("Say 'B'", model="google/gemma-3n-e2b-it:free", max_tokens=5),
                client.simple_completion("Say 'C'", model="google/gemma-3n-e2b-it:free", max_tokens=5),
            ]
            
            results = await asyncio.gather(*tasks)
            print("   🚀 Concurrent results:")
            for i, result in enumerate(results):
                print(f"      {i+1}. {result.strip()}")
            
            print("\n✅ All async tests completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Async test failed: {e}")
        return False


async def main():
    """Main async function."""
    success = await test_async_api()
    print(f"\n🦈 Async Test {'PASSED' if success else 'FAILED'}")


if __name__ == "__main__":
    asyncio.run(main())