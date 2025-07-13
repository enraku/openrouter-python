#!/usr/bin/env python3
"""Model Analysis Report Viewer - Display and filter model analysis results."""

import json
import os
from typing import Dict, List, Optional


class ModelReportViewer:
    """View and filter model analysis reports."""
    
    def __init__(self, report_file: str = "model_analysis_report.json"):
        self.report_file = report_file
        self.report = self.load_report()
    
    def load_report(self) -> Dict:
        """Load analysis report from JSON file."""
        if not os.path.exists(self.report_file):
            print(f"❌ Report file {self.report_file} not found")
            return {}
        
        with open(self.report_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def print_metadata(self):
        """Print report metadata."""
        metadata = self.report.get("metadata", {})
        print("🦈 Model Analysis Report")
        print("=" * 50)
        print(f"Generated: {metadata.get('timestamp', 'Unknown')}")
        print(f"Total models: {metadata.get('total_models', 0)}")
        print(f"Available models: {metadata.get('available_models', 0)}")
        print(f"Free models: {metadata.get('free_models', 0)}")
    
    def get_models(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Get models with optional filters."""
        models = self.report.get("models", [])
        
        if not filters:
            return models
        
        filtered = []
        for model in models:
            include = True
            
            # Filter by availability
            if "available_only" in filters and filters["available_only"]:
                if not model["availability"]["available"]:
                    include = False
            
            # Filter by free models
            if "free_only" in filters and filters["free_only"]:
                if not model["pricing"]["is_free"]:
                    include = False
            
            # Filter by minimum Japanese score
            if "min_japanese_score" in filters:
                score = model["quality"]["japanese_score"]
                if score is None or score < filters["min_japanese_score"]:
                    include = False
            
            # Filter by minimum speed
            if "min_tokens_per_second" in filters:
                speed = model["performance"]["tokens_per_second"]
                if speed is None or speed < filters["min_tokens_per_second"]:
                    include = False
            
            # Filter by model name pattern
            if "name_contains" in filters:
                if filters["name_contains"].lower() not in model["id"].lower():
                    include = False
            
            if include:
                filtered.append(model)
        
        return filtered
    
    def print_model_summary(self, model: Dict):
        """Print a summary of a single model."""
        print(f"\n🤖 {model['id']}")
        print(f"   Name: {model['name']}")
        
        # Pricing
        pricing = model["pricing"]
        if pricing["is_free"]:
            print(f"   💰 Cost: FREE")
        else:
            print(f"   💰 Cost: ${pricing['cost_per_1k_tokens']:.4f}/1K tokens")
        
        # Context length
        if model["context_length"]:
            print(f"   📏 Context: {model['context_length']:,} tokens")
        
        # Performance
        perf = model["performance"]
        if perf["avg_response_time"]:
            print(f"   ⚡ Speed: {perf['avg_response_time']:.2f}s response, {perf['tokens_per_second']:.1f} tok/s")
        
        # Quality scores
        quality = model["quality"]
        if quality["japanese_score"] is not None:
            print(f"   🇯🇵 Japanese: {quality['japanese_score']:.2f}/1.0")
        if quality["instruction_following"] is not None:
            print(f"   📋 Instructions: {quality['instruction_following']:.2f}/1.0")
        
        # Availability
        if not model["availability"]["available"]:
            print(f"   ❌ Status: Unavailable ({model['availability']['error_message']})")
        else:
            print(f"   ✅ Status: Available")
    
    def show_top_models(self, category: str, limit: int = 5):
        """Show top models in a specific category."""
        available_models = self.get_models({"available_only": True})
        
        if category == "japanese":
            sorted_models = sorted(
                [m for m in available_models if m["quality"]["japanese_score"] is not None],
                key=lambda x: x["quality"]["japanese_score"],
                reverse=True
            )[:limit]
            print(f"\n🇯🇵 Top {limit} Japanese Models:")
            
        elif category == "speed":
            sorted_models = sorted(
                [m for m in available_models if m["performance"]["tokens_per_second"] is not None],
                key=lambda x: x["performance"]["tokens_per_second"],
                reverse=True
            )[:limit]
            print(f"\n⚡ Top {limit} Fastest Models:")
            
        elif category == "free":
            sorted_models = [m for m in available_models if m["pricing"]["is_free"]][:limit]
            print(f"\n🆓 Top {limit} Free Models:")
            
        elif category == "instructions":
            sorted_models = sorted(
                [m for m in available_models if m["quality"]["instruction_following"] is not None],
                key=lambda x: x["quality"]["instruction_following"],
                reverse=True
            )[:limit]
            print(f"\n📋 Top {limit} Instruction-Following Models:")
            
        else:
            print(f"❌ Unknown category: {category}")
            return
        
        for i, model in enumerate(sorted_models, 1):
            print(f"\n{i}. {model['id']}")
            if category == "japanese" and model["quality"]["japanese_score"]:
                print(f"   Score: {model['quality']['japanese_score']:.2f}")
            elif category == "speed" and model["performance"]["tokens_per_second"]:
                print(f"   Speed: {model['performance']['tokens_per_second']:.1f} tokens/sec")
            elif category == "instructions" and model["quality"]["instruction_following"]:
                print(f"   Score: {model['quality']['instruction_following']:.2f}")
            
            # Show cost
            if model["pricing"]["is_free"]:
                print(f"   Cost: FREE")
            else:
                print(f"   Cost: ${model['pricing']['cost_per_1k_tokens']:.4f}/1K tokens")
    
    def show_cost_analysis(self):
        """Show cost analysis across models."""
        models = self.get_models({"available_only": True})
        
        free_models = [m for m in models if m["pricing"]["is_free"]]
        paid_models = [m for m in models if not m["pricing"]["is_free"]]
        
        print(f"\n💰 Cost Analysis:")
        print(f"Free models: {len(free_models)}")
        print(f"Paid models: {len(paid_models)}")
        
        if paid_models:
            costs = [m["pricing"]["cost_per_1k_tokens"] for m in paid_models]
            costs.sort()
            
            print(f"\nPaid model pricing (per 1K tokens):")
            print(f"   Cheapest: ${costs[0]:.6f}")
            print(f"   Most expensive: ${costs[-1]:.6f}")
            print(f"   Average: ${sum(costs)/len(costs):.6f}")
            
            # Show cheapest paid models
            cheapest = sorted(paid_models, key=lambda x: x["pricing"]["cost_per_1k_tokens"])[:3]
            print(f"\n💸 Cheapest paid models:")
            for i, model in enumerate(cheapest, 1):
                print(f"   {i}. {model['id']} - ${model['pricing']['cost_per_1k_tokens']:.6f}/1K")
    
    def interactive_search(self):
        """Interactive model search interface."""
        print("\n🔍 Interactive Model Search")
        print("Available filters:")
        print("1. Free models only")
        print("2. Minimum Japanese score")
        print("3. Minimum speed (tokens/sec)")
        print("4. Model name contains")
        print("5. Show all available models")
        print("6. Exit")
        
        while True:
            choice = input("\nChoose filter (1-6): ").strip()
            
            if choice == "1":
                models = self.get_models({"available_only": True, "free_only": True})
                print(f"\n🆓 Found {len(models)} free models:")
                for model in models[:10]:  # Show first 10
                    self.print_model_summary(model)
                
            elif choice == "2":
                try:
                    min_score = float(input("Minimum Japanese score (0-1): "))
                    models = self.get_models({
                        "available_only": True,
                        "min_japanese_score": min_score
                    })
                    print(f"\n🇯🇵 Found {len(models)} models with Japanese score >= {min_score}:")
                    for model in models[:10]:
                        self.print_model_summary(model)
                except ValueError:
                    print("❌ Invalid score format")
                
            elif choice == "3":
                try:
                    min_speed = float(input("Minimum tokens per second: "))
                    models = self.get_models({
                        "available_only": True,
                        "min_tokens_per_second": min_speed
                    })
                    print(f"\n⚡ Found {len(models)} models with speed >= {min_speed} tok/s:")
                    for model in models[:10]:
                        self.print_model_summary(model)
                except ValueError:
                    print("❌ Invalid speed format")
                
            elif choice == "4":
                search_term = input("Model name contains: ").strip()
                models = self.get_models({
                    "available_only": True,
                    "name_contains": search_term
                })
                print(f"\n🔍 Found {len(models)} models containing '{search_term}':")
                for model in models[:10]:
                    self.print_model_summary(model)
                
            elif choice == "5":
                models = self.get_models({"available_only": True})
                print(f"\n📋 All {len(models)} available models:")
                for model in models[:20]:  # Show first 20
                    self.print_model_summary(model)
                
            elif choice == "6":
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice")


def main():
    """Main function for report viewer."""
    print("🦈 OpenRouter Model Report Viewer")
    
    # Check if report exists
    if not os.path.exists("model_analysis_report.json"):
        print("❌ No analysis report found!")
        print("📝 Run 'python model_analyzer.py' first to generate a report")
        return
    
    viewer = ModelReportViewer()
    
    # Show metadata
    viewer.print_metadata()
    
    # Show various top lists
    viewer.show_top_models("japanese", 3)
    viewer.show_top_models("speed", 3)
    viewer.show_top_models("free", 5)
    viewer.show_top_models("instructions", 3)
    
    # Show cost analysis
    viewer.show_cost_analysis()
    
    # Interactive search
    response = input("\n🔍 Start interactive search? (y/N): ")
    if response.lower() in ['y', 'yes']:
        viewer.interactive_search()


if __name__ == "__main__":
    main()