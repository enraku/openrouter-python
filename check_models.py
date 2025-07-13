#!/usr/bin/env python3
"""Check available models and find free ones."""

import os
from openrouter_py import OpenRouterClient


def check_available_models():
    """Check available models and find free/cheap ones."""
    print("🦈 Checking available models...")
    
    try:
        with OpenRouterClient() as client:
            models = client.get_models()
            
            print(f"📋 Total models: {len(models.data)}")
            
            # Find free models
            free_models = []
            cheap_models = []
            
            for model in models.data:
                model_id = model.id
                pricing = model.pricing
                
                if pricing:
                    # Check if it's free (pricing might be $0)
                    prompt_cost = pricing.get("prompt", "0")
                    completion_cost = pricing.get("completion", "0")
                    
                    if prompt_cost == "0" and completion_cost == "0":
                        free_models.append(model_id)
                    elif float(prompt_cost) < 0.001 and float(completion_cost) < 0.001:
                        cheap_models.append(model_id)
            
            print(f"\n🆓 Free models ({len(free_models)}):")
            for model in free_models[:10]:  # Show first 10
                print(f"   - {model}")
            
            print(f"\n💰 Very cheap models ({len(cheap_models)}):")
            for model in cheap_models[:10]:  # Show first 10
                print(f"   - {model}")
            
            # Show some general models for testing
            print(f"\n🤖 Some popular models for testing:")
            popular_models = [
                "openai/gpt-3.5-turbo",
                "anthropic/claude-3-haiku",
                "google/gemma-2-2b-it",
                "meta-llama/llama-3.2-3b-instruct",
            ]
            
            for model_id in popular_models:
                found = any(m.id == model_id for m in models.data)
                status = "✅ Available" if found else "❌ Not found"
                print(f"   {model_id}: {status}")
                
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    check_available_models()