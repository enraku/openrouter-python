#!/usr/bin/env python3
"""Simple model testing tool for OpenRouter - avoids rate limits."""

import asyncio
import json
import os
import time
from typing import Dict, List

from openrouter_py import OpenRouterClient


async def test_single_model(model_id: str) -> Dict:
    """Test a single model with minimal requests."""
    print(f"🧪 Testing {model_id}")
    
    result = {
        "id": model_id,
        "available": False,
        "response_time": None,
        "response_quality": None,
        "japanese_capable": False,
        "error": None
    }
    
    try:
        with OpenRouterClient() as client:
            # Single test request
            start_time = time.time()
            
            response = client.simple_completion(
                "Hello! Please respond in both English and Japanese (日本語).",
                model=model_id,
                max_tokens=50
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            result["available"] = True
            result["response_time"] = response_time
            result["response_quality"] = len(response.strip())
            
            # Check for Japanese characters
            has_hiragana = any('\u3040' <= char <= '\u309F' for char in response)
            has_katakana = any('\u30A0' <= char <= '\u30FF' for char in response)
            has_kanji = any('\u4E00' <= char <= '\u9FAF' for char in response)
            
            result["japanese_capable"] = has_hiragana or has_katakana or has_kanji
            
            print(f"   ✅ Response time: {response_time:.2f}s, Japanese: {result['japanese_capable']}")
            return result
            
    except Exception as e:
        result["error"] = str(e)
        print(f"   ❌ Failed: {str(e)[:50]}...")
        return result


async def test_free_models():
    """Test free models with delays to avoid rate limits."""
    print("🦈 Testing Free OpenRouter Models (Rate-Limited)")
    
    # Get model list
    try:
        with OpenRouterClient() as client:
            models_response = client.get_models()
            print(f"📋 Found {len(models_response.data)} total models")
    except Exception as e:
        print(f"❌ Failed to get models: {e}")
        return
    
    # Filter free models
    free_models = [m for m in models_response.data if ":free" in m.id]
    print(f"🆓 Found {len(free_models)} free models")
    
    # Test first 5 free models with delays
    test_models = free_models[:5]
    results = []
    
    for i, model in enumerate(test_models):
        print(f"\n📦 Testing {i+1}/{len(test_models)}: {model.id}")
        
        result = await test_single_model(model.id)
        results.append(result)
        
        # Wait between tests to respect rate limits
        if i < len(test_models) - 1:
            print("⏳ Waiting 3 seconds...")
            await asyncio.sleep(3)
    
    # Generate simple report
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tested_models": len(results),
        "available_models": len([r for r in results if r["available"]]),
        "japanese_capable": len([r for r in results if r["japanese_capable"]]),
        "results": results
    }
    
    # Save report
    with open("simple_model_test_results.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print(f"\n📊 Test Summary:")
    print(f"=" * 40)
    print(f"Tested: {report['tested_models']} models")
    print(f"Available: {report['available_models']} models")
    print(f"Japanese capable: {report['japanese_capable']} models")
    
    available_results = [r for r in results if r["available"]]
    if available_results:
        avg_time = sum(r["response_time"] for r in available_results) / len(available_results)
        print(f"Average response time: {avg_time:.2f}s")
        
        print(f"\n⚡ Fastest models:")
        sorted_by_speed = sorted(available_results, key=lambda x: x["response_time"])
        for r in sorted_by_speed[:3]:
            print(f"   {r['id']}: {r['response_time']:.2f}s")
        
        japanese_models = [r for r in available_results if r["japanese_capable"]]
        if japanese_models:
            print(f"\n🇯🇵 Japanese-capable models:")
            for r in japanese_models:
                print(f"   {r['id']}: {r['response_time']:.2f}s")
    
    print(f"\n💾 Results saved to simple_model_test_results.json")


async def main():
    """Main function."""
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ Please set OPENROUTER_API_KEY environment variable")
        return
    
    await test_free_models()
    print("\n✅ Simple model testing completed!")


if __name__ == "__main__":
    asyncio.run(main())