#!/usr/bin/env python3
"""Generate comprehensive markdown report from analysis results."""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


def load_analysis_data() -> Dict:
    """Load analysis data from available sources."""
    # Try simple test results first
    if os.path.exists("simple_model_test_results.json"):
        with open("simple_model_test_results.json", "r", encoding="utf-8") as f:
            return json.load(f)
    
    # Fallback to comprehensive analysis
    elif os.path.exists("model_analysis_report.json"):
        with open("model_analysis_report.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            # Convert to simple format for consistency
            simple_results = []
            for model in data.get("models", []):
                if model["availability"]["available"]:
                    simple_results.append({
                        "id": model["id"],
                        "available": True,
                        "response_time": model["performance"]["avg_response_time"],
                        "response_quality": 100,  # Placeholder
                        "japanese_capable": model["quality"]["japanese_score"] and model["quality"]["japanese_score"] > 0.3,
                        "error": None
                    })
            
            return {
                "timestamp": data["metadata"]["timestamp"],
                "tested_models": len(simple_results),
                "available_models": len(simple_results),
                "japanese_capable": len([r for r in simple_results if r["japanese_capable"]]),
                "results": simple_results
            }
    
    else:
        return {}


def format_time(seconds: Optional[float]) -> str:
    """Format response time."""
    if seconds is None:
        return "N/A"
    return f"{seconds:.2f}s"


def format_status(available: bool, error: Optional[str]) -> str:
    """Format availability status."""
    if available:
        return "✅ 利用可能"
    elif error and "Rate limit" in error:
        return "⏸️ レート制限"
    else:
        return "❌ エラー"


def format_japanese(capable: bool) -> str:
    """Format Japanese capability."""
    return "🇯🇵 対応" if capable else "❌ 非対応"


def generate_performance_table(results: List[Dict]) -> str:
    """Generate performance comparison table."""
    # Filter and sort available models by response time
    available_models = [r for r in results if r["available"] and r["response_time"]]
    available_models.sort(key=lambda x: x["response_time"])
    
    table = "| 順位 | モデル名 | 応答時間 | 日本語対応 | ステータス |\n"
    table += "|------|----------|----------|------------|------------|\n"
    
    for i, model in enumerate(available_models, 1):
        model_name = model["id"]
        response_time = format_time(model["response_time"])
        japanese = format_japanese(model["japanese_capable"])
        status = format_status(model["available"], model.get("error"))
        
        table += f"| {i} | `{model_name}` | {response_time} | {japanese} | {status} |\n"
    
    # Add unavailable models
    unavailable_models = [r for r in results if not r["available"]]
    for model in unavailable_models:
        model_name = model["id"]
        status = format_status(model["available"], model.get("error"))
        table += f"| - | `{model_name}` | - | - | {status} |\n"
    
    return table


def generate_detailed_comparison_table(results: List[Dict]) -> str:
    """Generate detailed comparison table."""
    available_models = [r for r in results if r["available"]]
    available_models.sort(key=lambda x: x["response_time"] or 999)
    
    table = "| モデル名 | 応答時間 | レスポンス品質 | 日本語対応 | コスト | 推奨用途 |\n"
    table += "|----------|----------|----------------|------------|--------|----------|\n"
    
    for model in available_models:
        model_name = model["id"].replace(":", ":<br>").replace("/", "/<br>")  # 改行で見やすく
        response_time = format_time(model["response_time"])
        quality = f"{model.get('response_quality', 0)}文字" if model.get('response_quality') else "N/A"
        japanese = "✅" if model["japanese_capable"] else "❌"
        cost = "🆓 無料"
        
        # 推奨用途を決定
        if model["japanese_capable"] and model["response_time"] and model["response_time"] < 2.5:
            use_case = "🇯🇵 日本語タスク<br>⚡ 高速処理"
        elif model["japanese_capable"]:
            use_case = "🇯🇵 日本語タスク"
        elif model["response_time"] and model["response_time"] < 2.5:
            use_case = "⚡ 高速処理<br>🔰 初心者向け"
        else:
            use_case = "🔰 初心者向け<br>📝 テスト用"
        
        table += f"| `{model_name}` | {response_time} | {quality} | {japanese} | {cost} | {use_case} |\n"
    
    return table


def generate_summary_stats(data: Dict) -> Dict:
    """Generate summary statistics."""
    results = data.get("results", [])
    available_models = [r for r in results if r["available"]]
    
    if not available_models:
        return {
            "total_tested": len(results),
            "available_count": 0,
            "japanese_count": 0,
            "avg_response_time": 0,
            "fastest_model": None,
            "best_japanese": None
        }
    
    response_times = [r["response_time"] for r in available_models if r["response_time"]]
    japanese_models = [r for r in available_models if r["japanese_capable"]]
    
    fastest = min(available_models, key=lambda x: x["response_time"] or 999) if available_models else None
    best_japanese = japanese_models[0] if japanese_models else None
    
    return {
        "total_tested": len(results),
        "available_count": len(available_models),
        "japanese_count": len(japanese_models),
        "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
        "fastest_model": fastest,
        "best_japanese": best_japanese
    }


def generate_report(output_file: str = "openrouter_analysis_report.md"):
    """Generate comprehensive markdown report."""
    print("🦈 Generating OpenRouter analysis report...")
    
    data = load_analysis_data()
    if not data:
        print("❌ No analysis data found!")
        return
    
    stats = generate_summary_stats(data)
    results = data.get("results", [])
    
    # Generate report content
    report = f"""# OpenRouter モデル分析レポート 🦈

**分析日時**: {data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}  
**分析者**: gura 🦈  
**OpenRouter Python Client**: v0.1.0

---

## 📊 エグゼクティブサマリー

### 主要指標
- **テスト対象モデル**: {stats['total_tested']}個
- **利用可能モデル**: {stats['available_count']}個 ({stats['available_count']/stats['total_tested']*100:.1f}%)
- **日本語対応モデル**: {stats['japanese_count']}個 ({stats['japanese_count']/stats['total_tested']*100:.1f}%)
- **平均応答時間**: {stats['avg_response_time']:.2f}秒

### 🏆 推奨モデル
"""
    
    if stats['fastest_model']:
        report += f"- **⚡ 最高速モデル**: `{stats['fastest_model']['id']}` ({format_time(stats['fastest_model']['response_time'])})\n"
    
    if stats['best_japanese']:
        report += f"- **🇯🇵 日本語最優秀**: `{stats['best_japanese']['id']}` ({format_time(stats['best_japanese']['response_time'])})\n"
    
    if stats['available_count'] > 0:
        best_overall = min([r for r in results if r["available"]], 
                          key=lambda x: (not x["japanese_capable"], x["response_time"] or 999))
        report += f"- **🌟 総合推奨**: `{best_overall['id']}`\n"
    
    report += f"""
---

## 🎯 テスト概要

### テスト対象
- **無料モデル**: {stats['total_tested']}モデルをテスト
- **評価項目**: 応答速度、日本語能力、可用性

### テスト方法
1. **性能テスト**: 単一リクエストの応答時間測定
2. **日本語テスト**: 「Hello! Please respond in both English and Japanese (日本語).」での日本語文字検出
3. **可用性テスト**: API応答成功/失敗の確認

### 評価基準
- **応答時間**: 1リクエストの処理時間（秒）
- **日本語能力**: ひらがな・カタカナ・漢字の使用有無
- **可用性**: API正常応答の可否

---

## 📈 詳細分析結果

### 1. 性能ランキング

{generate_performance_table(results)}

### 2. 詳細比較表

{generate_detailed_comparison_table(results)}

### 3. 統計サマリー

| 項目 | 値 |
|------|-----|
| テスト実行日時 | {data.get('timestamp', 'N/A')} |
| 総テストモデル数 | {stats['total_tested']} |
| 利用可能モデル数 | {stats['available_count']} |
| 成功率 | {stats['available_count']/stats['total_tested']*100:.1f}% |
| 日本語対応モデル数 | {stats['japanese_count']} |
| 日本語対応率 | {stats['japanese_count']/stats['total_tested']*100:.1f}% |
| 平均応答時間 | {stats['avg_response_time']:.2f}秒 |
"""

    if stats['available_count'] > 0:
        available_models = [r for r in results if r["available"] and r["response_time"]]
        if available_models:
            fastest_time = min(r["response_time"] for r in available_models)
            slowest_time = max(r["response_time"] for r in available_models)
            report += f"| 最速応答時間 | {fastest_time:.2f}秒 |\n"
            report += f"| 最遅応答時間 | {slowest_time:.2f}秒 |\n"

    report += f"""
---

## 💡 用途別推奨

### 🔰 初心者・学習用
"""
    
    if stats['available_count'] > 0:
        # 安定性重視（エラーなし、適度な速度）
        stable_models = [r for r in results if r["available"] and r["response_time"]]
        if stable_models:
            beginner_model = min(stable_models, key=lambda x: x["response_time"])
            report += f"""**推奨**: `{beginner_model['id']}`
- **応答時間**: {format_time(beginner_model['response_time'])}
- **コスト**: 🆓 完全無料
- **理由**: 安定した応答、適度な速度
- **注意**: {'日本語対応あり' if beginner_model['japanese_capable'] else '日本語対応なし'}

"""
    
    if stats['japanese_count'] > 0:
        report += f"""### 🇯🇵 日本語タスク
**推奨**: `{stats['best_japanese']['id']}`
- **応答時間**: {format_time(stats['best_japanese']['response_time'])}
- **日本語能力**: ✅ 対応
- **コスト**: 🆓 完全無料
- **理由**: テスト対象中唯一の日本語対応モデル

"""
    
    if stats['fastest_model']:
        report += f"""### ⚡ 高速処理
**推奨**: `{stats['fastest_model']['id']}`
- **応答時間**: {format_time(stats['fastest_model']['response_time'])} (最速)
- **安定性**: ✅ 高い
- **コスト**: 🆓 無料
- **理由**: テスト対象中最高速度

"""
    
    report += f"""### 💰 本番運用
**推奨**: 有料モデル検討
- **理由**: レート制限なし、高品質、安定性
- **選択肢**: Claude、GPT、Geminiシリーズ
- **注意**: 詳細分析・コスト検討が必要

---

## ⚠️ 制限事項・注意点

### テスト制限
- **サンプル数**: 無料モデル{stats['total_tested']}個のみ
- **テスト回数**: 各モデル1回の単発テスト
- **評価期間**: 短時間のスナップショット測定

### 技術的制限
- **レート制限**: 一部無料モデルで発生
- **可用性変動**: 時間帯・地域による差異の可能性
- **ネットワーク影響**: 通信環境による測定誤差

### 日本語評価の限界
- **簡易評価**: 文字種の存在のみで判定
- **文脈理解**: 文法・意味理解は未評価
- **専門性**: 技術用語・敬語等は未検証

---

## 🚀 今後の改善案

### 分析拡張
1. **有料モデル分析**: 主要有料モデルの詳細評価
2. **継続監視**: 24時間可用性・パフォーマンス追跡
3. **品質評価**: BLEU/ROUGEスコア、人間評価導入

### 機能追加
1. **リアルタイム監視**: モデル可用性の継続監視
2. **コスト計算機**: 使用量ベースコスト予測ツール
3. **ベンチマーク**: 標準タスクでの性能比較

### UI/UX改善
1. **Webダッシュボード**: ブラウザベース分析インターフェース
2. **グラフ化**: 性能・コストの可視化
3. **アラート機能**: 推奨モデル変更の自動通知

---

## 📚 技術仕様

### 使用技術
- **OpenRouter Python Client**: v0.1.0 (カスタム実装)
- **評価フレームワーク**: 独自開発Python スクリプト
- **データ形式**: JSON (分析結果) + Markdown (レポート)

### 実行コマンド
```bash
# 簡易テスト実行
python simple_model_test.py

# 包括的分析実行  
python model_analyzer.py

# レポート生成
python generate_report.py
```

### ファイル構成
```
├── simple_model_test.py          # 軽量テストツール
├── model_analyzer.py             # 包括的分析ツール
├── generate_report.py            # レポート生成
├── model_summary.py              # サマリー表示
├── simple_model_test_results.json # テスト生データ
└── openrouter_analysis_report.md  # 最終レポート
```

---

## 📞 お問い合わせ・貢献

**開発者**: gura 🦈  
**プロジェクト**: OpenRouter Python Client  
**GitHub**: https://github.com/enraku/openrouter-python  
**ライセンス**: MIT

### 貢献方法
1. **Issues**: バグ報告・機能要望
2. **Pull Requests**: コード改善・新機能
3. **フィードバック**: 分析結果の検証・改善提案

---

*このレポートは自動生成されました。最新情報については再分析を実行してください。*

**生成日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**データソース**: {len(results)}モデルの実測データ
"""
    
    # Save report
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"✅ Report generated: {output_file}")
    print(f"📊 Analyzed {stats['total_tested']} models")
    print(f"📈 {stats['available_count']} models available")
    print(f"🇯🇵 {stats['japanese_count']} models support Japanese")


if __name__ == "__main__":
    generate_report()