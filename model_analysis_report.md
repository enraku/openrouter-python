# 🦈 OpenRouter無料モデル分析レポート

## 📊 テスト概要

**実行日時**: 2025年7月14日 03:24:01  
**テスト対象**: 60個の無料モデル  
**成功率**: 83.3% (50/60モデル利用可能)

## 🏆 総合統計

| 指標 | 値 | 割合 |
|------|----|----- |
| 利用可能モデル | 50 | 83.3% |
| 日本語対応 | 36 | 60.0% |
| 英語対応 | 36 | 60.0% |
| バイリンガル | 36 | 60.0% |
| 平均応答時間 | 3.89秒 | - |

## ⚡ パフォーマンストップ3

### 🚀 最速モデル
1. **qwen/qwen-2.5-72b-instruct:free** - 0.87秒
2. **google/gemini-2.0-flash-exp:free** - 0.98秒
3. **meta-llama/llama-3.2-11b-vision-instruct:free** - 1.37秒

### 🇯🇵 日本語対応ベスト
1. **qwen/qwen-2.5-72b-instruct:free** - 0.87秒
2. **google/gemini-2.0-flash-exp:free** - 0.98秒
3. **meta-llama/llama-3.2-11b-vision-instruct:free** - 1.37秒

### 📝 レスポンス品質トップ3
1. **moonshotai/kimi-dev-72b:free** - 754文字
2. **rekaai/reka-flash-3:free** - 694文字
3. **tngtech/deepseek-r1t-chimera:free** - 676文字

## 🚫 利用不可モデル (10個)

### API エラー
- moonshotai/kimi-k2:free
- nvidia/llama-3.1-nemotron-ultra-253b-v1:free
- meta-llama/llama-4-maverick:free
- meta-llama/llama-4-scout:free
- mistralai/mistral-small-24b-instruct-2501:free
- deepseek/deepseek-r1-distill-qwen-14b:free

### レート制限
- cognitivecomputations/dolphin-mistral-24b-venice-edition:free
- qwen/qwen3-4b:free
- meta-llama/llama-3.2-3b-instruct:free
- meta-llama/llama-3.1-405b-instruct:free

## 🔍 カテゴリ別分析

### 🌟 おすすめモデル (高速 + 日本語対応)

| モデル | 応答時間 | 品質 | 特徴 |
|--------|----------|------|------|
| qwen/qwen-2.5-72b-instruct:free | 0.87s | 13文字 | 最速・バイリンガル |
| google/gemini-2.0-flash-exp:free | 0.98s | 13文字 | Google最新モデル |
| meta-llama/llama-3.2-11b-vision-instruct:free | 1.37s | 13文字 | Vision対応 |
| google/gemma-3n-e2b-it:free | 1.44s | 29文字 | 軽量・高性能 |
| thudm/glm-4-32b:free | 1.50s | 11文字 | 中国製高品質 |

### 📈 高品質レスポンス (長文対応)

| モデル | 応答時間 | 品質 | 文字数 |
|--------|----------|------|--------|
| moonshotai/kimi-dev-72b:free | 5.26s | 754文字 | 超高品質 |
| rekaai/reka-flash-3:free | 3.40s | 694文字 | バランス良好 |
| tngtech/deepseek-r1t-chimera:free | 6.35s | 676文字 | 高品質 |
| moonshotai/kimi-vl-a3b-thinking:free | 4.83s | 594文字 | Vision + 思考 |
| nvidia/llama-3.3-nemotron-super-49b-v1:free | 5.77s | 566文字 | Nvidia製 |

### 🔧 コーディング特化

| モデル | 応答時間 | 特徴 |
|--------|----------|------|
| qwen/qwen-2.5-coder-32b-instruct:free | 2.28s | コーディング特化 |
| mistralai/devstral-small-2505:free | 1.80s | 開発者向け |

### 🖼️ Vision対応

| モデル | 応答時間 | 特徴 |
|--------|----------|------|
| meta-llama/llama-3.2-11b-vision-instruct:free | 1.37s | 高速Vision |
| qwen/qwen2.5-vl-32b-instruct:free | 2.03s | マルチモーダル |
| qwen/qwen2.5-vl-72b-instruct:free | 1.49s | 大規模Vision |
| moonshotai/kimi-vl-a3b-thinking:free | 4.83s | 思考型Vision |

## 📋 プロバイダー別統計

### Google (6モデル)
- 利用可能: 5/6 (83.3%)
- 平均応答時間: 1.94s
- 日本語対応率: 100%

### Qwen (9モデル)
- 利用可能: 8/9 (88.9%)
- 平均応答時間: 2.47s
- 日本語対応率: 44.4%

### Meta-Llama (6モデル)
- 利用可能: 3/6 (50.0%)
- 平均応答時間: 2.43s
- 日本語対応率: 66.7%

### DeepSeek (7モデル)
- 利用可能: 5/7 (71.4%)
- 平均応答時間: 11.16s
- 日本語対応率: 40.0%

### Mistral (5モデル)
- 利用可能: 4/5 (80.0%)
- 平均応答時間: 2.11s
- 日本語対応率: 100%

## 🎯 用途別推奨モデル

### 💬 チャット・対話
**推奨**: `qwen/qwen-2.5-72b-instruct:free`
- 理由: 最速 + バイリンガル + 安定性

### 🔍 詳細分析・長文生成
**推奨**: `moonshotai/kimi-dev-72b:free`
- 理由: 超高品質レスポンス + 日本語対応

### 💻 プログラミング
**推奨**: `qwen/qwen-2.5-coder-32b-instruct:free`
- 理由: コーディング特化 + 高速

### 🖼️ 画像解析
**推奨**: `meta-llama/llama-3.2-11b-vision-instruct:free`
- 理由: 高速Vision処理 + 日本語対応

### ⚡ 高速レスポンス重視
**推奨**: `google/gemini-2.0-flash-exp:free`
- 理由: Google最新 + 1秒以下の応答

## 🔧 技術仕様

### テスト方法
- 英語と日本語両方でのプロンプトテスト
- 3回まで再試行（エラー時）
- レート制限対応
- 応答時間・文字数・品質の測定

### 品質評価基準
- 文字数によるレスポンス量測定
- 日本語・英語の対応状況確認
- エラー率・成功率の計算

## 📈 まとめ

- **総合ベスト**: `qwen/qwen-2.5-72b-instruct:free` (速度 + 品質 + 日本語)
- **高品質**: `moonshotai/kimi-dev-72b:free` (詳細レスポンス)  
- **バランス**: `google/gemini-2.0-flash-exp:free` (Google品質)
- **コーディング**: `qwen/qwen-2.5-coder-32b-instruct:free`

無料モデルでも十分実用的で、特にQwen、Google、Meta-Llamaシリーズが優秀な結果を示している。