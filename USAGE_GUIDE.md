# 🦈 OpenRouter Python Library 使用ガイド

## 他プロジェクトからの使用方法

### 1. PyPIからインストール（公開後）

```bash
# pipでインストール
pip install openrouter-py

# または uv でインストール
uv add openrouter-py
```

### 2. GitHubから直接インストール（現在推奨）

```bash
# pip
pip install git+https://github.com/enraku/openrouter-python.git

# uv
uv add git+https://github.com/enraku/openrouter-python.git

# 特定のブランチやタグを指定
pip install git+https://github.com/enraku/openrouter-python.git@main
```

### 3. ローカル開発用（editable install）

```bash
# ローカルにクローン
git clone https://github.com/enraku/openrouter-python.git
cd openrouter-python

# pip editable install
pip install -e .

# uv でのローカル参照
uv add --editable /path/to/openrouter-python
```

## プロジェクトでの設定例

### pyproject.toml（uv使用時）

```toml
[project]
name = "your-project"
version = "0.1.0"
dependencies = [
    "openrouter-py @ git+https://github.com/enraku/openrouter-python.git",
]

# または特定のバージョン指定
dependencies = [
    "openrouter-py @ git+https://github.com/enraku/openrouter-python.git@v0.1.0",
]
```

### requirements.txt（pip使用時）

```txt
# GitHubから
git+https://github.com/enraku/openrouter-python.git

# ローカルから（開発時）
-e /path/to/openrouter-python
```

## 基本的な使い方

### 1. シンプルな使用例

```python
from openrouter_py import OpenRouterClient

# APIキーは環境変数 OPENROUTER_API_KEY から自動読み込み
client = OpenRouterClient()

# または直接指定
client = OpenRouterClient(api_key="your-api-key")

# 簡単な質問
response = client.simple_completion(
    "こんにちは！元気ですか？",
    model="google/gemini-2.0-flash-exp:free"  # 無料モデル
)
print(response)
```

### 2. チャット形式での使用

```python
from openrouter_py import OpenRouterClient, ChatMessage

client = OpenRouterClient()

messages = [
    ChatMessage(role="system", content="あなたは親切なアシスタントです"),
    ChatMessage(role="user", content="Python でファイルを読む方法を教えて")
]

completion = client.chat_completion(
    messages=messages,
    model="qwen/qwen-2.5-72b-instruct:free",  # 高速無料モデル
    max_tokens=500
)

print(completion.content)
```

### 3. ストリーミングレスポンス

```python
from openrouter_py import OpenRouterClient, ChatMessage

client = OpenRouterClient()

# ストリーミングで回答を取得
for chunk in client.stream_completion(
    messages=[ChatMessage(role="user", content="長い物語を書いて")],
    model="mistralai/mistral-nemo:free"
):
    print(chunk.content, end="", flush=True)
```

### 4. 非同期クライアント

```python
import asyncio
from openrouter_py import AsyncOpenRouterClient, ChatMessage

async def main():
    client = AsyncOpenRouterClient()
    
    # 非同期で複数のリクエストを並行処理
    tasks = []
    prompts = ["質問1", "質問2", "質問3"]
    
    for prompt in prompts:
        task = client.chat_completion_async(
            messages=[ChatMessage(role="user", content=prompt)],
            model="google/gemini-2.0-flash-exp:free"
        )
        tasks.append(task)
    
    responses = await asyncio.gather(*tasks)
    for response in responses:
        print(response.content)

asyncio.run(main())
```

### 5. エラーハンドリング

```python
from openrouter_py import OpenRouterClient
from openrouter_py.exceptions import RateLimitError, APIError

client = OpenRouterClient()

try:
    response = client.simple_completion(
        "Hello!",
        model="some-model"
    )
except RateLimitError as e:
    print(f"レート制限エラー: {e}")
    # リトライロジックなど
except APIError as e:
    print(f"APIエラー: {e}")
except Exception as e:
    print(f"予期しないエラー: {e}")
```

### 6. モデル情報の取得

```python
from openrouter_py import OpenRouterClient

client = OpenRouterClient()

# 利用可能なモデル一覧
models = client.list_models()

# 無料モデルのみフィルタ
free_models = [m for m in models if m.is_free]

# 日本語対応モデルを探す
japanese_models = [
    m for m in models 
    if "japanese" in m.description.lower() or "日本語" in m.description
]

for model in free_models[:5]:
    print(f"{model.id}: {model.name} (Context: {model.context_length})")
```

## 環境変数の設定

### Bashで設定
```bash
# .env ファイル
OPENROUTER_API_KEY=your-api-key-here

# または exportで設定
export OPENROUTER_API_KEY=your-api-key-here
```

### Python内で設定
```python
import os

# 方法1: os.environ で直接設定
os.environ['OPENROUTER_API_KEY'] = 'your-api-key-here'

# 方法2: python-dotenv を使用（推奨）
from dotenv import load_dotenv
load_dotenv()  # .env ファイルから自動読み込み

# 方法3: 複数の方法を試す
def setup_api_key():
    # 1. 環境変数
    if os.getenv('OPENROUTER_API_KEY'):
        return
    
    # 2. .env ファイル
    load_dotenv()
    if os.getenv('OPENROUTER_API_KEY'):
        return
    
    # 3. 設定ファイル
    config_path = Path.home() / '.openrouter_key'
    if config_path.exists():
        os.environ['OPENROUTER_API_KEY'] = config_path.read_text().strip()
```

詳しい例は [examples/environment_setup.py](./examples/environment_setup.py) を参照。

## 推奨モデル（無料）

| 用途 | モデルID | 特徴 |
|------|----------|------|
| 高速レスポンス | `qwen/qwen-2.5-72b-instruct:free` | 最速、日本語対応 |
| 高品質 | `google/gemini-2.0-flash-exp:free` | Google最新、バランス良 |
| 長文生成 | `moonshotai/kimi-dev-72b:free` | 超高品質レスポンス |
| コーディング | `qwen/qwen-2.5-coder-32b-instruct:free` | プログラミング特化 |
| Vision | `meta-llama/llama-3.2-11b-vision-instruct:free` | 画像解析対応 |

## トラブルシューティング

### インストールエラー

```bash
# 依存関係の問題がある場合
pip install --upgrade pip
pip install -r requirements.txt

# uvの場合
uv sync
```

### API キーエラー

```python
# デバッグ用：APIキーが設定されているか確認
import os
print(f"API Key set: {'OPENROUTER_API_KEY' in os.environ}")
```

### レート制限対策

```python
import time
from openrouter_py.exceptions import RateLimitError

def retry_on_rate_limit(func, max_retries=3):
    for i in range(max_retries):
        try:
            return func()
        except RateLimitError:
            if i < max_retries - 1:
                wait_time = 2 ** i  # 指数バックオフ
                time.sleep(wait_time)
            else:
                raise
```

## さらに詳しい情報

- 📚 [APIドキュメント](./docs/_build/html/index.html)
- 💡 [サンプルコード](./examples/)
- 🔍 [モデル分析レポート](./model_analysis_report.md)
- 🐛 [Issue報告](https://github.com/enraku/openrouter-python/issues)