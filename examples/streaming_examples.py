#!/usr/bin/env python3
"""Streaming examples for OpenRouter Python client."""

import asyncio
import os
import time
from typing import List

from openrouter_py import AsyncOpenRouterClient, OpenRouterClient
from openrouter_py.models.chat import ChatMessage


def basic_streaming():
    """Basic streaming example."""
    print("🌊 Basic Streaming")
    
    with OpenRouterClient() as client:
        print("Prompt: Tell me a short story about a robot")
        print("Response: ", end="", flush=True)
        
        full_response = ""
        for chunk in client.simple_completion_stream(
            "Tell me a short story about a robot",
            model="google/gemma-3n-e2b-it:free",
            max_tokens=100
        ):
            print(chunk, end="", flush=True)
            full_response += chunk
            time.sleep(0.05)  # Visual delay for demo
        
        print(f"\n\n📝 Full response length: {len(full_response)} characters")


def streaming_chat():
    """Streaming chat completion."""
    print("\n💬 Streaming Chat")
    
    with OpenRouterClient() as client:
        messages: List[ChatMessage] = [
            ChatMessage(role="user", content="Explain quantum computing briefly")
        ]
        
        print("User: Explain quantum computing briefly")
        print("Assistant: ", end="", flush=True)
        
        chunk_count = 0
        for chunk in client.chat_completion_stream(
            messages=messages,
            model="mistralai/mistral-small-3.2-24b-instruct:free",
            max_tokens=150
        ):
            if chunk.content:
                print(chunk.content, end="", flush=True)
                chunk_count += 1
                time.sleep(0.03)
        
        print(f"\n\n📊 Received {chunk_count} chunks")


def streaming_with_status():
    """Streaming with status monitoring."""
    print("\n📊 Streaming with Status")
    
    with OpenRouterClient() as client:
        print("Generating response with status updates...")
        
        content_chunks = []
        chunk_count = 0
        
        for chunk in client.chat_completion_stream(
            messages=[ChatMessage(role="user", content="List 5 benefits of exercise")],
            model="google/gemma-3n-e2b-it:free",
            max_tokens=120
        ):
            chunk_count += 1
            
            if chunk.content:
                content_chunks.append(chunk.content)
                print(f"[{chunk_count:3d}] {chunk.content}", end="", flush=True)
            
            if chunk.is_finished:
                print(f"\n✅ Stream finished at chunk {chunk_count}")
                break
            
            time.sleep(0.02)
        
        print(f"\n📋 Total content chunks: {len(content_chunks)}")


async def async_streaming():
    """Async streaming example."""
    print("\n🚀 Async Streaming")
    
    async with AsyncOpenRouterClient() as client:
        print("Async prompt: Describe the future of AI in 3 sentences")
        print("Response: ", end="", flush=True)
        
        word_count = 0
        async for chunk in client.simple_completion_stream(
            "Describe the future of AI in 3 sentences",
            model="mistralai/mistral-small-3.2-24b-instruct:free",
            max_tokens=100
        ):
            print(chunk, end="", flush=True)
            word_count += len(chunk.split())
            await asyncio.sleep(0.04)
        
        print(f"\n\n📈 Approximate word count: {word_count}")


async def concurrent_streaming():
    """Multiple concurrent streams."""
    print("\n⚡ Concurrent Streaming")
    
    async def stream_with_label(client, prompt, label):
        """Stream with a label for identification."""
        result = ""
        print(f"\n{label} starting...")
        
        async for chunk in client.simple_completion_stream(
            prompt,
            model="google/gemma-3n-e2b-it:free",
            max_tokens=50
        ):
            result += chunk
        
        print(f"{label} complete: {result[:50]}...")
        return f"{label}: {result}"
    
    async with AsyncOpenRouterClient() as client:
        # Start multiple streams concurrently
        tasks = [
            stream_with_label(client, "Name 3 colors", "🎨 Colors"),
            stream_with_label(client, "Name 3 animals", "🐾 Animals"),
            stream_with_label(client, "Name 3 countries", "🌍 Countries")
        ]
        
        results = await asyncio.gather(*tasks)
        
        print("\n📋 All streams completed:")
        for result in results:
            print(f"   {result}")


def interactive_streaming():
    """Interactive streaming demo."""
    print("\n🎮 Interactive Streaming")
    
    with OpenRouterClient() as client:
        while True:
            user_input = input("\n💬 You (or 'quit' to exit): ")
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            print("🤖 Assistant: ", end="", flush=True)
            
            try:
                for chunk in client.simple_completion_stream(
                    user_input,
                    model="google/gemma-3n-e2b-it:free",
                    max_tokens=80,
                    temperature=0.7
                ):
                    print(chunk, end="", flush=True)
                    time.sleep(0.02)
                print()  # New line after response
                
            except KeyboardInterrupt:
                print("\n⚠️  Stream interrupted")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")


def streaming_comparison():
    """Compare streaming vs non-streaming."""
    print("\n⚖️  Streaming vs Non-Streaming Comparison")
    
    prompt = "Explain machine learning in simple terms"
    
    with OpenRouterClient() as client:
        # Non-streaming
        print("📦 Non-streaming (wait for complete response):")
        start_time = time.time()
        regular_response = client.simple_completion(
            prompt,
            model="google/gemma-3n-e2b-it:free",
            max_tokens=80
        )
        regular_time = time.time() - start_time
        print(f"Response: {regular_response}")
        print(f"⏱️  Time: {regular_time:.2f}s")
        
        print("\n🌊 Streaming (real-time response):")
        start_time = time.time()
        print("Response: ", end="", flush=True)
        
        streaming_response = ""
        for chunk in client.simple_completion_stream(
            prompt,
            model="google/gemma-3n-e2b-it:free",
            max_tokens=80
        ):
            print(chunk, end="", flush=True)
            streaming_response += chunk
            time.sleep(0.03)
        
        streaming_time = time.time() - start_time
        print(f"\n⏱️  Time: {streaming_time:.2f}s")
        
        print(f"\n📊 Comparison:")
        print(f"   Regular: {len(regular_response)} chars in {regular_time:.2f}s")
        print(f"   Streaming: {len(streaming_response)} chars in {streaming_time:.2f}s")


async def main():
    """Run all streaming examples."""
    print("🦈 OpenRouter Streaming Examples")
    
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ Please set OPENROUTER_API_KEY environment variable")
        return
    
    basic_streaming()
    streaming_chat()
    streaming_with_status()
    await async_streaming()
    await concurrent_streaming()
    streaming_comparison()
    
    # Interactive example last (optional)
    response = input("\n🎮 Run interactive streaming demo? (y/N): ")
    if response.lower() in ['y', 'yes']:
        interactive_streaming()
    
    print("\n✅ All streaming examples completed!")


if __name__ == "__main__":
    asyncio.run(main())