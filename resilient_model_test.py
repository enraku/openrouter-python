#!/usr/bin/env python3
"""Resilient model testing - handles failures and resumes from where it left off."""

import asyncio
import json
import os
import time
from typing import Dict, List, Optional
from dataclasses import dataclass

from openrouter_py import OpenRouterClient


@dataclass
class TestProgress:
    """Track testing progress for resumption."""
    total_models: int
    completed_models: List[str]
    failed_models: List[str]
    results: List[Dict]
    last_saved: float
    
    def save(self, filename: str = "test_progress.json"):
        """Save progress to file."""
        data = {
            "total_models": self.total_models,
            "completed_models": self.completed_models,
            "failed_models": self.failed_models,
            "results": self.results,
            "last_saved": time.time()
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, filename: str = "test_progress.json") -> Optional['TestProgress']:
        """Load progress from file."""
        if not os.path.exists(filename):
            return None
        
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            return cls(
                total_models=data["total_models"],
                completed_models=data["completed_models"],
                failed_models=data["failed_models"],
                results=data["results"],
                last_saved=data["last_saved"]
            )
        except Exception as e:
            print(f"⚠️ Failed to load progress: {e}")
            return None


class ResilientModelTester:
    """Resilient model tester with resume capability."""
    
    def __init__(self):
        self.progress = TestProgress(0, [], [], [], 0)
        self.save_interval = 5  # Save progress every 5 tests
        self.retry_delay = 3    # Wait 3 seconds between retries
        self.max_retries = 2    # Max retries per model
    
    def load_progress(self) -> bool:
        """Load existing progress if available."""
        saved_progress = TestProgress.load()
        if saved_progress:
            self.progress = saved_progress
            print(f"📁 Loaded progress: {len(self.progress.completed_models)}/{self.progress.total_models} completed")
            return True
        return False
    
    def get_remaining_models(self, all_model_ids: List[str]) -> List[str]:
        """Get list of models that still need testing."""
        completed_set = set(self.progress.completed_models)
        failed_set = set(self.progress.failed_models)
        tested_set = completed_set | failed_set
        
        remaining = [model_id for model_id in all_model_ids if model_id not in tested_set]
        return remaining
    
    async def test_single_model(self, model_id: str) -> Optional[Dict]:
        """Test a single model with retries."""
        for attempt in range(self.max_retries + 1):
            try:
                result = await self._do_model_test(model_id, attempt + 1)
                return result
                
            except Exception as e:
                error_msg = str(e)
                
                if attempt < self.max_retries:
                    if "rate limit" in error_msg.lower():
                        wait_time = (attempt + 1) * self.retry_delay
                        print(f"    ⏸️ Rate limited, retrying in {wait_time}s (attempt {attempt + 1}/{self.max_retries + 1})")
                        await asyncio.sleep(wait_time)
                    else:
                        print(f"    ⚠️ Error, retrying: {error_msg[:30]}...")
                        await asyncio.sleep(1)
                else:
                    print(f"    ❌ Failed after {self.max_retries + 1} attempts: {error_msg[:50]}...")
                    return {
                        "id": model_id,
                        "available": False,
                        "response_time": None,
                        "response_quality": None,
                        "japanese_capable": False,
                        "english_capable": False,
                        "error": error_msg,
                        "test_timestamp": time.time(),
                        "attempts": attempt + 1
                    }
        
        return None
    
    async def _do_model_test(self, model_id: str, attempt: int) -> Dict:
        """Perform the actual model test."""
        print(f"  🧪 Testing {model_id} (attempt {attempt})")
        
        result = {
            "id": model_id,
            "available": False,
            "response_time": None,
            "response_quality": None,
            "japanese_capable": False,
            "english_capable": False,
            "error": None,
            "test_timestamp": time.time(),
            "attempts": attempt
        }
        
        with OpenRouterClient() as client:
            start_time = time.time()
            
            # Comprehensive test prompt
            response = client.simple_completion(
                "Hello! Please respond in both English and Japanese. Say 'Hello' in English and 'こんにちは' in Japanese.",
                model=model_id,
                max_tokens=150,
                temperature=0.7
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            result["available"] = True
            result["response_time"] = response_time
            result["response_quality"] = len(response.strip())
            
            # Enhanced language detection
            response_lower = response.lower()
            
            # English detection
            english_indicators = [
                'hello', 'hi', 'greetings', 'good', 'english', 'language',
                'morning', 'afternoon', 'evening', 'welcome', 'nice'
            ]
            result["english_capable"] = any(word in response_lower for word in english_indicators)
            
            # Japanese detection
            has_hiragana = any('\u3040' <= char <= '\u309F' for char in response)
            has_katakana = any('\u30A0' <= char <= '\u30FF' for char in response)
            has_kanji = any('\u4E00' <= char <= '\u9FAF' for char in response)
            
            # Specific Japanese words
            japanese_words = ['こんにちは', 'おはよう', 'こんばんは', '日本語', 'ありがとう']
            has_japanese_words = any(word in response for word in japanese_words)
            
            result["japanese_capable"] = has_hiragana or has_katakana or has_kanji or has_japanese_words
            
            # Status indicators
            status = "✅" if result["available"] else "❌"
            jp_status = "🇯🇵" if result["japanese_capable"] else "🌍"
            en_status = "🇺🇸" if result["english_capable"] else "❓"
            
            print(f"    {status} {en_status}{jp_status} {response_time:.2f}s - {len(response)} chars")
            
            return result
    
    async def test_all_models(self, model_ids: List[str], resume: bool = True):
        """Test all models with progress tracking and resumption."""
        if resume and self.load_progress():
            if self.progress.total_models != len(model_ids):
                print("⚠️ Model list changed, starting fresh")
                self.progress = TestProgress(len(model_ids), [], [], [], 0)
            else:
                remaining_models = self.get_remaining_models(model_ids)
                print(f"🔄 Resuming from previous session")
                print(f"   Completed: {len(self.progress.completed_models)}")
                print(f"   Failed: {len(self.progress.failed_models)}")
                print(f"   Remaining: {len(remaining_models)}")
                model_ids = remaining_models
        else:
            self.progress = TestProgress(len(model_ids), [], [], [], 0)
            print(f"🆕 Starting fresh test of {len(model_ids)} models")
        
        if not model_ids:
            print("✅ All models already tested!")
            return self.progress.results
        
        print(f"🚀 Testing {len(model_ids)} models...")
        
        for i, model_id in enumerate(model_ids, 1):
            print(f"\n📦 Progress: {i}/{len(model_ids)} - {model_id}")
            
            result = await self.test_single_model(model_id)
            
            if result:
                self.progress.results.append(result)
                
                if result["available"]:
                    self.progress.completed_models.append(model_id)
                else:
                    self.progress.failed_models.append(model_id)
                
                # Save progress periodically
                if i % self.save_interval == 0 or i == len(model_ids):
                    self.progress.save()
                    completed_total = len(self.progress.completed_models)
                    failed_total = len(self.progress.failed_models)
                    print(f"    💾 Progress saved: ✅{completed_total} ❌{failed_total}")
            
            # Small delay between tests
            await asyncio.sleep(0.5)
        
        print(f"\n🎉 Testing completed!")
        return self.progress.results
    
    def generate_final_report(self):
        """Generate comprehensive final report."""
        results = self.progress.results
        available_results = [r for r in results if r["available"]]
        japanese_results = [r for r in results if r["japanese_capable"]]
        english_results = [r for r in results if r["english_capable"]]
        bilingual_results = [r for r in results if r["japanese_capable"] and r["english_capable"]]
        
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        report = {
            "metadata": {
                "timestamp": timestamp,
                "test_type": "comprehensive_free_models",
                "total_tested": len(results),
                "total_available": len(available_results),
                "total_japanese": len(japanese_results),
                "total_english": len(english_results),
                "total_bilingual": len(bilingual_results),
                "success_rate": len(available_results) / len(results) * 100 if results else 0,
                "japanese_rate": len(japanese_results) / len(results) * 100 if results else 0
            },
            "results": results
        }
        
        # Save comprehensive report
        with open("comprehensive_model_analysis.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print(f"\n📊 Final Report Summary:")
        print(f"=" * 60)
        print(f"Total models tested: {len(results)}")
        print(f"Available models: {len(available_results)} ({len(available_results)/len(results)*100:.1f}%)")
        print(f"Japanese capable: {len(japanese_results)} ({len(japanese_results)/len(results)*100:.1f}%)")
        print(f"English capable: {len(english_results)} ({len(english_results)/len(results)*100:.1f}%)")
        print(f"Bilingual models: {len(bilingual_results)} ({len(bilingual_results)/len(results)*100:.1f}%)")
        
        if available_results:
            avg_time = sum(r["response_time"] for r in available_results) / len(available_results)
            print(f"Average response time: {avg_time:.2f}s")
            
            # Top performers by category
            print(f"\n🏆 Top Performers:")
            
            # Fastest overall
            fastest = min(available_results, key=lambda x: x["response_time"])
            print(f"⚡ Fastest: {fastest['id']} ({fastest['response_time']:.2f}s)")
            
            # Best Japanese
            if japanese_results:
                fastest_jp = min(japanese_results, key=lambda x: x["response_time"])
                print(f"🇯🇵 Best Japanese: {fastest_jp['id']} ({fastest_jp['response_time']:.2f}s)")
            
            # Best bilingual
            if bilingual_results:
                fastest_bi = min(bilingual_results, key=lambda x: x["response_time"])
                print(f"🌐 Best Bilingual: {fastest_bi['id']} ({fastest_bi['response_time']:.2f}s)")
        
        print(f"\n💾 Comprehensive report saved to: comprehensive_model_analysis.json")
        
        # Clean up progress file
        if os.path.exists("test_progress.json"):
            os.remove("test_progress.json")
            print("🧹 Cleaned up progress file")
        
        return report


async def main():
    """Main function."""
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ Please set OPENROUTER_API_KEY environment variable")
        return
    
    print("🦈 Resilient OpenRouter Model Testing")
    print("This will test ALL free models with resume capability")
    
    # Get all free models
    try:
        with OpenRouterClient() as client:
            models_response = client.get_models()
            all_models = models_response.data
    except Exception as e:
        print(f"❌ Failed to get model list: {e}")
        return
    
    free_models = [m for m in all_models if ":free" in m.id]
    free_model_ids = [m.id for m in free_models]
    
    print(f"📋 Found {len(all_models)} total models")
    print(f"🆓 Found {len(free_models)} free models")
    print(f"🎯 Will test all {len(free_models)} free models")
    
    # Check for existing progress
    if os.path.exists("test_progress.json"):
        resume = input("📁 Found previous progress. Resume? (Y/n): ").strip().lower()
        resume = resume != 'n'
    else:
        resume = False
    
    if not resume:
        confirm = input(f"🚀 Start testing {len(free_models)} models? This may take a while... (y/N): ").strip().lower()
        if confirm != 'y':
            print("👋 Cancelled")
            return
    
    # Start testing
    tester = ResilientModelTester()
    results = await tester.test_all_models(free_model_ids, resume=resume)
    
    # Generate final report
    final_report = tester.generate_final_report()
    
    print(f"\n✅ All testing completed!")
    print(f"📊 Final stats: {final_report['metadata']['total_available']}/{final_report['metadata']['total_tested']} models available")


if __name__ == "__main__":
    asyncio.run(main())