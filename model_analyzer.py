#!/usr/bin/env python3
"""OpenRouter Model Analyzer - Comprehensive model evaluation tool."""

import asyncio
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from openrouter_py import AsyncOpenRouterClient, OpenRouterClient
from openrouter_py.models.chat import ChatMessage


@dataclass
class ModelAnalysis:
    """Comprehensive model analysis results."""
    id: str
    name: str
    description: Optional[str]
    context_length: Optional[int]
    pricing: Optional[Dict]
    
    # Cost analysis
    prompt_cost: float = 0.0
    completion_cost: float = 0.0
    cost_per_1k_tokens: float = 0.0
    is_free: bool = False
    
    # Performance metrics
    avg_response_time: Optional[float] = None
    tokens_per_second: Optional[float] = None
    success_rate: Optional[float] = None
    
    # Quality metrics
    japanese_score: Optional[float] = None
    coherence_score: Optional[float] = None
    instruction_following: Optional[float] = None
    
    # Availability
    available: bool = True
    error_message: Optional[str] = None


class ModelAnalyzer:
    """Analyzes OpenRouter models across multiple dimensions."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("API key required")
        
        self.client = OpenRouterClient(api_key=self.api_key)
        self.async_client = AsyncOpenRouterClient(api_key=self.api_key)
        self.models: List[ModelAnalysis] = []
    
    def get_all_models(self) -> List[ModelAnalysis]:
        """Fetch and analyze all available models."""
        print("🦈 Fetching all OpenRouter models...")
        
        try:
            models_response = self.client.get_models()
            print(f"📋 Found {len(models_response.data)} models")
            
            for model_data in models_response.data:
                analysis = ModelAnalysis(
                    id=model_data.id,
                    name=model_data.name,
                    description=model_data.description,
                    context_length=model_data.context_length,
                    pricing=model_data.pricing
                )
                
                # Analyze pricing
                self._analyze_pricing(analysis)
                
                self.models.append(analysis)
            
            print(f"✅ Processed {len(self.models)} models")
            return self.models
            
        except Exception as e:
            print(f"❌ Error fetching models: {e}")
            return []
    
    def _analyze_pricing(self, analysis: ModelAnalysis):
        """Analyze model pricing information."""
        if not analysis.pricing:
            analysis.is_free = ":free" in analysis.id
            return
        
        try:
            prompt_cost_str = analysis.pricing.get("prompt", "0")
            completion_cost_str = analysis.pricing.get("completion", "0")
            
            analysis.prompt_cost = float(prompt_cost_str)
            analysis.completion_cost = float(completion_cost_str)
            
            # Calculate average cost per 1K tokens
            analysis.cost_per_1k_tokens = (analysis.prompt_cost + analysis.completion_cost) / 2
            
            # Check if it's free
            analysis.is_free = (analysis.prompt_cost == 0.0 and analysis.completion_cost == 0.0)
            
        except (ValueError, TypeError):
            analysis.is_free = ":free" in analysis.id
    
    async def test_model_performance(self, model_id: str, test_count: int = 3) -> Tuple[float, float, float]:
        """Test model performance: response time, tokens/sec, success rate."""
        print(f"🧪 Testing performance: {model_id}")
        
        test_prompts = [
            "What is 2+2?",
            "Name three colors.",
            "Hello, how are you?"
        ]
        
        response_times = []
        token_rates = []
        successes = 0
        
        for i in range(test_count):
            prompt = test_prompts[i % len(test_prompts)]
            
            try:
                start_time = time.time()
                
                completion = await self.async_client.chat_completion(
                    messages=[ChatMessage(role="user", content=prompt)],
                    model=model_id,
                    max_tokens=50
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                response_times.append(response_time)
                
                # Calculate tokens per second
                if completion.usage and completion.usage.total_tokens > 0:
                    tokens_per_sec = completion.usage.total_tokens / response_time
                    token_rates.append(tokens_per_sec)
                
                successes += 1
                
                # Small delay between requests
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"   ⚠️ Test {i+1} failed: {str(e)[:50]}...")
                continue
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        avg_token_rate = sum(token_rates) / len(token_rates) if token_rates else 0
        success_rate = successes / test_count
        
        return avg_response_time, avg_token_rate, success_rate
    
    async def test_japanese_ability(self, model_id: str) -> float:
        """Test Japanese language capabilities."""
        print(f"🇯🇵 Testing Japanese: {model_id}")
        
        japanese_tests = [
            {
                "prompt": "こんにちは。日本語で自己紹介してください。",
                "expected_keywords": ["こんにちは", "です", "ます"]
            },
            {
                "prompt": "「桜」を使って短い詩を作ってください。",
                "expected_keywords": ["桜", "春", "花"]
            },
            {
                "prompt": "次の文を敬語に変えてください：「先生が来る」",
                "expected_keywords": ["いらっしゃ", "お越し", "先生"]
            }
        ]
        
        total_score = 0
        test_count = len(japanese_tests)
        
        for test in japanese_tests:
            try:
                completion = await self.async_client.chat_completion(
                    messages=[ChatMessage(role="user", content=test["prompt"])],
                    model=model_id,
                    max_tokens=100
                )
                
                response = completion.content or ""
                
                # Score based on Japanese content and keywords
                score = 0
                
                # Basic Japanese character check
                if any('\u3040' <= char <= '\u309F' for char in response):  # Hiragana
                    score += 0.3
                if any('\u30A0' <= char <= '\u30FF' for char in response):  # Katakana
                    score += 0.2
                if any('\u4E00' <= char <= '\u9FAF' for char in response):  # Kanji
                    score += 0.3
                
                # Keyword presence
                keyword_score = sum(1 for keyword in test["expected_keywords"] 
                                  if keyword in response) / len(test["expected_keywords"])
                score += keyword_score * 0.2
                
                total_score += min(score, 1.0)
                
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"   ⚠️ Japanese test failed: {str(e)[:30]}...")
                continue
        
        return total_score / test_count if test_count > 0 else 0.0
    
    async def test_instruction_following(self, model_id: str) -> float:
        """Test how well the model follows instructions."""
        print(f"📋 Testing instruction following: {model_id}")
        
        instruction_tests = [
            {
                "prompt": "Answer with exactly one word: What color is the sky?",
                "check": lambda r: len(r.split()) == 1 and "blue" in r.lower()
            },
            {
                "prompt": "List exactly 3 animals, numbered 1-3:",
                "check": lambda r: r.count('1.') == 1 and r.count('2.') == 1 and r.count('3.') == 1
            },
            {
                "prompt": "Respond only with 'YES' or 'NO': Is Tokyo in Japan?",
                "check": lambda r: r.strip().upper() in ['YES', 'NO']
            }
        ]
        
        score = 0
        for test in instruction_tests:
            try:
                completion = await self.async_client.chat_completion(
                    messages=[ChatMessage(role="user", content=test["prompt"])],
                    model=model_id,
                    max_tokens=50
                )
                
                response = completion.content or ""
                if test["check"](response):
                    score += 1
                
                await asyncio.sleep(0.5)
                
            except Exception:
                continue
        
        return score / len(instruction_tests)
    
    async def analyze_models_batch(self, model_ids: List[str], batch_size: int = 5):
        """Analyze multiple models in batches."""
        print(f"🔬 Analyzing {len(model_ids)} models in batches of {batch_size}")
        
        for i in range(0, len(model_ids), batch_size):
            batch = model_ids[i:i + batch_size]
            print(f"\n📦 Processing batch {i//batch_size + 1}: {len(batch)} models")
            
            # Find the corresponding analysis objects
            batch_analyses = [analysis for analysis in self.models if analysis.id in batch]
            
            # Run tests for each model in the batch
            for analysis in batch_analyses:
                try:
                    print(f"\n🧪 Testing {analysis.id}")
                    
                    # Performance test
                    response_time, token_rate, success_rate = await self.test_model_performance(analysis.id)
                    analysis.avg_response_time = response_time
                    analysis.tokens_per_second = token_rate
                    analysis.success_rate = success_rate
                    
                    # Only test further if model is responsive
                    if success_rate > 0:
                        # Japanese ability test
                        analysis.japanese_score = await self.test_japanese_ability(analysis.id)
                        
                        # Instruction following test
                        analysis.instruction_following = await self.test_instruction_following(analysis.id)
                        
                        analysis.available = True
                        print(f"✅ {analysis.id} completed")
                    else:
                        analysis.available = False
                        analysis.error_message = "Model not responding"
                        print(f"❌ {analysis.id} not available")
                
                except Exception as e:
                    analysis.available = False
                    analysis.error_message = str(e)
                    print(f"❌ {analysis.id} failed: {e}")
            
            # Delay between batches to respect rate limits
            if i + batch_size < len(model_ids):
                print("⏳ Waiting between batches...")
                await asyncio.sleep(5)
    
    def generate_report(self, filename: str = "model_analysis_report.json"):
        """Generate comprehensive analysis report."""
        print(f"📊 Generating analysis report...")
        
        report = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_models": len(self.models),
                "available_models": len([m for m in self.models if m.available]),
                "free_models": len([m for m in self.models if m.is_free])
            },
            "models": []
        }
        
        for model in self.models:
            model_data = {
                "id": model.id,
                "name": model.name,
                "description": model.description,
                "context_length": model.context_length,
                "pricing": {
                    "prompt_cost": model.prompt_cost,
                    "completion_cost": model.completion_cost,
                    "cost_per_1k_tokens": model.cost_per_1k_tokens,
                    "is_free": model.is_free
                },
                "performance": {
                    "avg_response_time": model.avg_response_time,
                    "tokens_per_second": model.tokens_per_second,
                    "success_rate": model.success_rate
                },
                "quality": {
                    "japanese_score": model.japanese_score,
                    "instruction_following": model.instruction_following
                },
                "availability": {
                    "available": model.available,
                    "error_message": model.error_message
                }
            }
            report["models"].append(model_data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Report saved to {filename}")
        return report
    
    def print_summary(self):
        """Print analysis summary."""
        available_models = [m for m in self.models if m.available]
        free_models = [m for m in self.models if m.is_free and m.available]
        
        print(f"\n📊 Analysis Summary")
        print(f"=" * 50)
        print(f"Total models: {len(self.models)}")
        print(f"Available models: {len(available_models)}")
        print(f"Free models: {len(free_models)}")
        
        if available_models:
            # Top performers
            japanese_sorted = sorted([m for m in available_models if m.japanese_score], 
                                   key=lambda x: x.japanese_score, reverse=True)[:5]
            speed_sorted = sorted([m for m in available_models if m.tokens_per_second], 
                                key=lambda x: x.tokens_per_second, reverse=True)[:5]
            
            print(f"\n🇯🇵 Top Japanese models:")
            for i, model in enumerate(japanese_sorted[:3], 1):
                print(f"   {i}. {model.id} (Score: {model.japanese_score:.2f})")
            
            print(f"\n⚡ Fastest models:")
            for i, model in enumerate(speed_sorted[:3], 1):
                print(f"   {i}. {model.id} ({model.tokens_per_second:.1f} tokens/sec)")
    
    def close(self):
        """Clean up resources."""
        self.client.close()


async def main():
    """Main analysis function."""
    print("🦈 OpenRouter Model Analysis Tool")
    
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ Please set OPENROUTER_API_KEY environment variable")
        return
    
    analyzer = ModelAnalyzer()
    
    try:
        # Get all models
        models = analyzer.get_all_models()
        
        if not models:
            print("❌ No models found")
            return
        
        # Analyze free models first (faster and cheaper)
        free_model_ids = [m.id for m in models if m.is_free][:10]  # Limit to first 10 free models
        
        print(f"🆓 Found {len([m for m in models if m.is_free])} free models")
        print(f"🧪 Testing first {len(free_model_ids)} free models...")
        
        if free_model_ids:
            await analyzer.analyze_models_batch(free_model_ids, batch_size=3)
        
        # Generate report
        report = analyzer.generate_report()
        analyzer.print_summary()
        
        print(f"\n✅ Analysis completed!")
        print(f"📁 Results saved to model_analysis_report.json")
        
    finally:
        analyzer.close()


if __name__ == "__main__":
    asyncio.run(main())