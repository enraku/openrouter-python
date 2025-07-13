#!/usr/bin/env python3
"""Basic usage examples for OpenRouter Python client."""

import os
from openrouter_py import OpenRouterClient


def main():
    """Demonstrate basic OpenRouter client usage."""
    print("🦈 OpenRouter Basic Usage Examples")
    
    # Check API key
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ Please set OPENROUTER_API_KEY environment variable")
        return
    
    # Initialize client (API key from environment)
    with OpenRouterClient() as client:
        
        print("\n1️⃣ Simple Text Completion")
        response = client.simple_completion(
            "Explain Python in one sentence.",
            model="google/gemma-3n-e2b-it:free",
            max_tokens=50
        )
        print(f"Response: {response}")
        
        print("\n2️⃣ Check Account Balance")
        balance = client.get_balance()
        print(f"💰 Remaining credits: ${balance.balance:.4f}")
        print(f"📊 Total purchased: ${balance.total_purchased:.2f}")
        print(f"💸 Total used: ${balance.total_used:.4f}")
        
        print("\n3️⃣ List Available Models")
        models = client.get_models()
        print(f"📋 Found {len(models.data)} models")
        
        # Show first 5 free models
        free_models = [m for m in models.data if ":free" in m.id][:5]
        print("🆓 First 5 free models:")
        for model in free_models:
            print(f"   - {model.id}")
        
        print("\n4️⃣ Custom Parameters")
        response = client.simple_completion(
            "List 3 programming languages briefly:",
            model="mistralai/mistral-small-3.2-24b-instruct:free",
            max_tokens=100,
            temperature=0.7  # More creative
        )
        print(f"Creative response: {response}")
        
        print("\n✅ Basic usage examples completed!")


if __name__ == "__main__":
    main()