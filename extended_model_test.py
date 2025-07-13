#!/usr/bin/env python3
"""Extended model testing - test more models with smart rate limiting."""

import asyncio
import json
import os
import time
from typing import Dict, List
import random

from openrouter_py import OpenRouterClient


async def test_model_batch(model_ids: List[str], batch_size: int = 3, delay: int = 5) -> List[Dict]:
    """Test multiple models in batches with delays."""
    print(f"🦈 Testing {len(model_ids)} models in batches of {batch_size}")
    
    all_results = []
    
    for i in range(0, len(model_ids), batch_size):
        batch = model_ids[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(model_ids) + batch_size - 1) // batch_size
        
        print(f"\n📦 Batch {batch_num}/{total_batches}: Testing {len(batch)} models")
        
        batch_results = []
        for model_id in batch:
            result = await test_single_model(model_id)
            batch_results.append(result)
            
            # Small delay between models in same batch
            await asyncio.sleep(1)
        
        all_results.extend(batch_results)
        
        # Longer delay between batches
        if i + batch_size < len(model_ids):
            print(f"⏳ Waiting {delay} seconds before next batch...")
            await asyncio.sleep(delay)
    
    return all_results


async def test_single_model(model_id: str) -> Dict:
    """Test a single model with error handling."""
    print(f"  🧪 Testing {model_id}")
    
    result = {
        "id": model_id,
        "available": False,
        "response_time": None,
        "response_quality": None,
        "japanese_capable": False,
        "english_capable": False,
        "error": None,
        "test_timestamp": time.time()
    }
    
    try:
        with OpenRouterClient() as client:
            start_time = time.time()
            
            # Simple bilingual test
            response = client.simple_completion(
                "Hello! Please say hello in both English and Japanese.",
                model=model_id,
                max_tokens=100,
                temperature=0.7
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            result["available"] = True
            result["response_time"] = response_time
            result["response_quality"] = len(response.strip())
            
            # Check language capabilities
            response_lower = response.lower()
            
            # English detection
            english_words = ['hello', 'hi', 'greetings', 'good']
            result["english_capable"] = any(word in response_lower for word in english_words)
            
            # Japanese character detection
            has_hiragana = any('\u3040' <= char <= '\u309F' for char in response)
            has_katakana = any('\u30A0' <= char <= '\u30FF' for char in response)
            has_kanji = any('\u4E00' <= char <= '\u9FAF' for char in response)
            
            result["japanese_capable"] = has_hiragana or has_katakana or has_kanji
            
            status = "✅" if result["available"] else "❌"
            jp_status = "🇯🇵" if result["japanese_capable"] else "🌍"
            print(f"    {status} {jp_status} {response_time:.2f}s - {len(response)} chars")
            
            return result
            
    except Exception as e:
        error_msg = str(e)
        result["error"] = error_msg
        
        # Categorize error types
        if "rate limit" in error_msg.lower():
            print(f"    ⏸️ Rate limited")
        elif "not found" in error_msg.lower() or "model" in error_msg.lower():
            print(f"    ❓ Model unavailable")
        else:
            print(f"    ❌ Error: {error_msg[:30]}...")
        
        return result


async def comprehensive_model_test(target_count: int = 20):
    """Run comprehensive test on multiple free models."""
    print(f"🦈 Comprehensive Model Test (Target: {target_count} models)")
    
    # Get all free models
    try:
        with OpenRouterClient() as client:
            models_response = client.get_models()
            all_models = models_response.data
    except Exception as e:
        print(f"❌ Failed to get model list: {e}")
        return
    
    # Filter free models
    free_models = [m for m in all_models if ":free" in m.id]
    print(f"📋 Found {len(all_models)} total models, {len(free_models)} free models")
    
    # Select models to test
    if len(free_models) > target_count:
        # Mix of strategies: some random, some from different providers
        selected_models = []
        
        # Get models from different providers
        providers = {}
        for model in free_models:
            provider = model.id.split('/')[0]
            if provider not in providers:
                providers[provider] = []
            providers[provider].append(model)
        
        # Take 1-2 models from each provider
        for provider, models in providers.items():
            selected_models.extend(models[:2])
        
        # Fill remaining with random selection
        remaining_models = [m for m in free_models if m not in selected_models]
        remaining_count = target_count - len(selected_models)
        
        if remaining_count > 0:
            random.shuffle(remaining_models)
            selected_models.extend(remaining_models[:remaining_count])
        
        test_models = selected_models[:target_count]
    else:
        test_models = free_models
    
    print(f"🎯 Selected {len(test_models)} models for testing")
    
    # Test models in batches
    model_ids = [m.id for m in test_models]
    results = await test_model_batch(model_ids, batch_size=3, delay=8)
    
    # Generate comprehensive report
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    report = {
        "timestamp": timestamp,
        "total_models_available": len(all_models),
        "free_models_available": len(free_models),
        "tested_models": len(results),
        "available_models": len([r for r in results if r["available"]]),
        "japanese_capable": len([r for r in results if r["japanese_capable"]]),
        "english_capable": len([r for r in results if r["english_capable"]]),
        "results": results
    }
    
    # Save detailed results
    with open("comprehensive_model_test_results.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Print summary
    available_results = [r for r in results if r["available"]]
    japanese_results = [r for r in results if r["japanese_capable"]]
    
    print(f"\n📊 Test Summary:")
    print(f"=" * 50)
    print(f"Total OpenRouter models: {len(all_models)}")
    print(f"Free models available: {len(free_models)}")
    print(f"Models tested: {len(results)}")
    print(f"Successfully tested: {len(available_results)} ({len(available_results)/len(results)*100:.1f}%)")
    print(f"Japanese capable: {len(japanese_results)} ({len(japanese_results)/len(results)*100:.1f}%)")
    
    if available_results:
        avg_time = sum(r["response_time"] for r in available_results) / len(available_results)
        print(f"Average response time: {avg_time:.2f}s")
        
        # Top performers
        sorted_by_speed = sorted(available_results, key=lambda x: x["response_time"])
        print(f"\n⚡ Top 5 fastest models:")
        for i, result in enumerate(sorted_by_speed[:5], 1):
            jp_flag = "🇯🇵" if result["japanese_capable"] else "🌍"
            print(f"  {i}. {result['id']} - {result['response_time']:.2f}s {jp_flag}")
        
        if japanese_results:
            print(f"\n🇯🇵 Japanese-capable models:")
            japanese_sorted = sorted(japanese_results, key=lambda x: x["response_time"])
            for i, result in enumerate(japanese_sorted, 1):
                print(f"  {i}. {result['id']} - {result['response_time']:.2f}s")
    
    print(f"\n💾 Detailed results saved to: comprehensive_model_test_results.json")
    return report


async def main():
    """Main function."""
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ Please set OPENROUTER_API_KEY environment variable")
        return
    
    # Ask user for test size
    print("🦈 OpenRouter Extended Model Testing")
    print("Available options:")
    print("1. Quick test (10 models)")
    print("2. Medium test (20 models)") 
    print("3. Comprehensive test (30 models)")
    print("4. Full free model test (all ~59 models)")
    
    choice = input("Choose option (1-4): ").strip()
    
    if choice == "1":
        target = 10
    elif choice == "2":
        target = 20
    elif choice == "3":
        target = 30
    elif choice == "4":
        target = 59
    else:
        target = 20  # Default
    
    await comprehensive_model_test(target)
    print("\n✅ Extended model testing completed!")


if __name__ == "__main__":
    asyncio.run(main())