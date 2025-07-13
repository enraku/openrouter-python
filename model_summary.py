#!/usr/bin/env python3
"""Model summary and recommendation tool."""

import json
import os
from typing import Dict, List


def load_model_data() -> Dict:
    """Load model data from analysis."""
    # Try to load comprehensive analysis first
    if os.path.exists("model_analysis_report.json"):
        with open("model_analysis_report.json", "r", encoding="utf-8") as f:
            return json.load(f)
    
    # Fallback to simple test results
    elif os.path.exists("simple_model_test_results.json"):
        with open("simple_model_test_results.json", "r", encoding="utf-8") as f:
            simple_data = json.load(f)
            
            # Convert to analysis format
            return {
                "metadata": {
                    "timestamp": simple_data["timestamp"],
                    "total_models": simple_data["tested_models"],
                    "available_models": simple_data["available_models"],
                    "free_models": simple_data["tested_models"]
                },
                "models": [
                    {
                        "id": r["id"],
                        "name": r["id"].split("/")[-1],
                        "pricing": {"is_free": True},
                        "performance": {
                            "avg_response_time": r["response_time"],
                            "success_rate": 1.0 if r["available"] else 0.0
                        },
                        "quality": {
                            "japanese_score": 0.5 if r["japanese_capable"] else 0.0
                        },
                        "availability": {
                            "available": r["available"],
                            "error_message": r["error"]
                        }
                    }
                    for r in simple_data["results"]
                ]
            }
    
    else:
        print("❌ No model data found!")
        return {}


def print_model_recommendations():
    """Print model recommendations for different use cases."""
    data = load_model_data()
    
    if not data:
        return
    
    models = data.get("models", [])
    available_models = [m for m in models if m["availability"]["available"]]
    
    print("🦈 OpenRouter Model Recommendations")
    print("=" * 50)
    
    metadata = data.get("metadata", {})
    print(f"Analysis date: {metadata.get('timestamp', 'Unknown')}")
    print(f"Total models analyzed: {metadata.get('total_models', 0)}")
    print(f"Available models: {len(available_models)}")
    
    if not available_models:
        print("❌ No available models found in analysis")
        return
    
    # Free models for budget-conscious users
    free_models = [m for m in available_models if m["pricing"]["is_free"]]
    if free_models:
        print(f"\n🆓 Best Free Models ({len(free_models)} available):")
        # Sort by response time
        fast_free = sorted([m for m in free_models if m["performance"]["avg_response_time"]], 
                          key=lambda x: x["performance"]["avg_response_time"])[:3]
        for i, model in enumerate(fast_free, 1):
            time_str = f"{model['performance']['avg_response_time']:.2f}s" if model['performance']['avg_response_time'] else "N/A"
            japanese_str = "🇯🇵" if model["quality"]["japanese_score"] and model["quality"]["japanese_score"] > 0.3 else ""
            print(f"   {i}. {model['id']} - {time_str} {japanese_str}")
    
    # Fast models
    fast_models = sorted([m for m in available_models if m["performance"]["avg_response_time"]], 
                        key=lambda x: x["performance"]["avg_response_time"])[:3]
    if fast_models:
        print(f"\n⚡ Fastest Models:")
        for i, model in enumerate(fast_models, 1):
            time_str = f"{model['performance']['avg_response_time']:.2f}s"
            free_str = "🆓" if model["pricing"]["is_free"] else "💰"
            print(f"   {i}. {model['id']} - {time_str} {free_str}")
    
    # Japanese-capable models
    japanese_models = [m for m in available_models 
                      if m["quality"]["japanese_score"] and m["quality"]["japanese_score"] > 0.3]
    if japanese_models:
        print(f"\n🇯🇵 Japanese-Capable Models ({len(japanese_models)} found):")
        for i, model in enumerate(japanese_models, 1):
            score_str = f"{model['quality']['japanese_score']:.2f}" if model["quality"]["japanese_score"] else "N/A"
            free_str = "🆓" if model["pricing"]["is_free"] else "💰"
            print(f"   {i}. {model['id']} - Score: {score_str} {free_str}")
    
    # Use case recommendations
    print(f"\n💡 Recommendations by Use Case:")
    print(f"=" * 30)
    
    # For beginners/testing
    if free_models:
        best_free = min(free_models, key=lambda x: x["performance"]["avg_response_time"] or 999)
        print(f"🔰 For beginners/testing: {best_free['id']}")
        print(f"   - Free to use")
        response_time = best_free['performance']['avg_response_time']
        if response_time:
            print(f"   - Response time: {response_time:.2f}s")
        else:
            print(f"   - Response time: Not measured")
    
    # For Japanese tasks
    if japanese_models:
        best_japanese = max(japanese_models, key=lambda x: x["quality"]["japanese_score"] or 0)
        print(f"🇯🇵 For Japanese tasks: {best_japanese['id']}")
        print(f"   - Japanese score: {best_japanese['quality']['japanese_score']:.2f}")
        free_str = "Free" if best_japanese["pricing"]["is_free"] else "Paid"
        print(f"   - Cost: {free_str}")
    
    # For speed-critical tasks
    if fast_models:
        fastest = fast_models[0]
        print(f"🚀 For speed-critical tasks: {fastest['id']}")
        response_time = fastest['performance']['avg_response_time']
        if response_time:
            print(f"   - Response time: {response_time:.2f}s")
        else:
            print(f"   - Response time: Not measured")
        free_str = "Free" if fastest["pricing"]["is_free"] else "Paid"
        print(f"   - Cost: {free_str}")
    
    # General recommendations
    print(f"\n📋 General Guidelines:")
    print(f"• Start with free models to test your application")
    print(f"• Consider response time vs. quality trade-offs")
    print(f"• Some models may have rate limits")
    print(f"• Test with your specific use case before committing")


def generate_model_comparison_table():
    """Generate a comparison table of top models."""
    data = load_model_data()
    
    if not data:
        return
    
    models = data.get("models", [])
    available_models = [m for m in models if m["availability"]["available"]]
    
    if not available_models:
        return
    
    print(f"\n📊 Model Comparison Table")
    print(f"=" * 80)
    
    # Table header
    print(f"{'Model':<40} {'Speed':<8} {'Japanese':<8} {'Cost':<6} {'Status'}")
    print(f"{'-'*40} {'-'*8} {'-'*8} {'-'*6} {'-'*6}")
    
    # Sort by response time
    sorted_models = sorted([m for m in available_models if m["performance"]["avg_response_time"]], 
                          key=lambda x: x["performance"]["avg_response_time"])
    
    for model in sorted_models[:10]:  # Top 10
        name = model["id"][:38] + "..." if len(model["id"]) > 40 else model["id"]
        
        speed = f"{model['performance']['avg_response_time']:.2f}s" if model['performance']['avg_response_time'] else "N/A"
        
        japanese_score = model["quality"]["japanese_score"]
        japanese = f"{japanese_score:.2f}" if japanese_score and japanese_score > 0 else "No"
        
        cost = "Free" if model["pricing"]["is_free"] else "Paid"
        
        status = "✅"
        
        print(f"{name:<40} {speed:<8} {japanese:<8} {cost:<6} {status}")


def main():
    """Main function."""
    print_model_recommendations()
    generate_model_comparison_table()
    
    print(f"\n🔄 To update analysis:")
    print(f"• Run 'python simple_model_test.py' for quick testing")
    print(f"• Run 'python model_analyzer.py' for comprehensive analysis")


if __name__ == "__main__":
    main()