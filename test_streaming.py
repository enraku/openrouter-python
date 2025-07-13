#!/usr/bin/env python3
"""Test streaming functionality."""

import asyncio
import os
import time
from typing import List

from openrouter_py import AsyncOpenRouterClient, OpenRouterClient
from openrouter_py.models.chat import ChatMessage


def test_sync_streaming():
    """Test synchronous streaming."""
    print("🦈 Testing Sync Streaming...")
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY environment variable not set")
        return False
    
    try:
        with OpenRouterClient() as client:
            print("\n🔄 Sync Simple Streaming:")
            print("Response: ", end="", flush=True)
            
            full_response = ""
            for chunk in client.simple_completion_stream(
                "Count from 1 to 5 slowly",
                model="google/gemma-3n-e2b-it:free",
                max_tokens=50
            ):
                print(chunk, end="", flush=True)
                full_response += chunk
                time.sleep(0.1)  # Visual delay
            
            print(f"\n✅ Full response: {full_response.strip()}")
            
            print("\n🔄 Sync Chat Streaming:")
            messages: List[ChatMessage] = [
                ChatMessage(role="user", content="Say hello in 3 different languages")
            ]
            
            print("Response: ", end="", flush=True)
            chunk_count = 0
            for chunk in client.chat_completion_stream(
                messages=messages,
                model="mistralai/mistral-small-3.2-24b-instruct:free",
                max_tokens=100
            ):
                if chunk.content:
                    print(chunk.content, end="", flush=True)
                chunk_count += 1
            
            print(f"\n✅ Received {chunk_count} chunks")
            return True
            
    except Exception as e:
        print(f"❌ Sync streaming test failed: {e}")
        return False


async def test_async_streaming():
    """Test asynchronous streaming."""
    print("\n🦈 Testing Async Streaming...")
    
    try:
        async with AsyncOpenRouterClient() as client:
            print("\n🔄 Async Simple Streaming:")
            print("Response: ", end="", flush=True)
            
            full_response = ""
            async for chunk in client.simple_completion_stream(
                "List 3 programming languages",
                model="google/gemma-3n-e2b-it:free",
                max_tokens=50
            ):
                print(chunk, end="", flush=True)
                full_response += chunk
                await asyncio.sleep(0.1)  # Visual delay
            
            print(f"\n✅ Full response: {full_response.strip()}")
            
            print("\n🔄 Async Chat Streaming:")
            messages: List[ChatMessage] = [
                ChatMessage(role="user", content="Name 3 colors briefly")
            ]
            
            print("Response: ", end="", flush=True)
            chunk_count = 0
            async for chunk in client.chat_completion_stream(
                messages=messages,
                model="mistralai/mistral-small-3.2-24b-instruct:free",
                max_tokens=50
            ):
                if chunk.content:
                    print(chunk.content, end="", flush=True)
                chunk_count += 1
            
            print(f"\n✅ Received {chunk_count} chunks")
            return True
            
    except Exception as e:
        print(f"❌ Async streaming test failed: {e}")
        return False


async def main():
    """Main test function."""
    print("🦈 Testing Streaming Features...")
    
    # Test sync streaming
    sync_success = test_sync_streaming()
    
    # Test async streaming
    async_success = await test_async_streaming()
    
    overall_success = sync_success and async_success
    print(f"\n🦈 Streaming Tests {'PASSED' if overall_success else 'FAILED'}")
    
    return overall_success


if __name__ == "__main__":
    asyncio.run(main())