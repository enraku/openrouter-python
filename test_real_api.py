#!/usr/bin/env python3
"""Real OpenRouter API testing script."""

import os
from typing import List

from openrouter_py import OpenRouterClient
from openrouter_py.models.chat import ChatMessage


def test_real_api():
    """Test all features with real OpenRouter API."""
    print("🦈 OpenRouter Real API Test Starting...")
    
    # Check API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY environment variable not set")
        return False
    
    try:
        with OpenRouterClient() as client:
            
            # Test 1: Get Balance
            print("\n1️⃣ Testing get_balance()...")
            balance = client.get_balance()
            print(f"   💰 Balance: ${balance.balance:.4f}")
            print(f"   💳 Total purchased: ${balance.total_purchased:.4f}")
            print(f"   💸 Total used: ${balance.total_used:.4f}")
            
            # Test 2: Get Models
            print("\n2️⃣ Testing get_models()...")
            models = client.get_models()
            print(f"   📋 Found {len(models.data)} models")
            # Show first 3 models
            for i, model in enumerate(models.data[:3]):
                print(f"   🤖 {i+1}. {model.id}")
            
            # Test 3: Simple Completion
            print("\n3️⃣ Testing simple_completion()...")
            response = client.simple_completion(
                "Say hello in Japanese in 1 short sentence.",
                model="google/gemma-3n-e2b-it:free",
                max_tokens=50
            )
            print(f"   🗣️ Response: {response}")
            
            # Test 4: Chat Completion with messages
            print("\n4️⃣ Testing chat_completion()...")
            messages: List[ChatMessage] = [
                ChatMessage(role="user", content="What is 2+2? Answer briefly.")
            ]
            completion = client.chat_completion(
                messages=messages,
                model="mistralai/mistral-small-3.2-24b-instruct:free",
                max_tokens=20,
                temperature=0.1
            )
            print(f"   💬 Chat response: {completion.content}")
            print(f"   📊 Tokens used: {completion.usage.total_tokens if completion.usage else 'N/A'}")
            
            print("\n✅ All real API tests completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_real_api()
    print(f"\n🦈 Test {'PASSED' if success else 'FAILED'}")