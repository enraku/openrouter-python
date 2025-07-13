#!/usr/bin/env python3
"""
環境変数の設定方法サンプル
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from openrouter_py import OpenRouterClient

# 方法1: os.environ で直接設定（現在のプロセスのみ）
def set_env_direct():
    """プログラム内で環境変数を設定"""
    # 設定
    os.environ['OPENROUTER_API_KEY'] = 'your-api-key-here'
    
    # 確認
    print(f"API Key set: {os.environ.get('OPENROUTER_API_KEY', 'Not set')}")
    
    # これで自動的に環境変数から読み込まれる
    client = OpenRouterClient()
    return client


# 方法2: python-dotenv を使用（推奠）
def setup_with_dotenv():
    """`.env` ファイルから環境変数を読み込む"""
    # .env ファイルを探して読み込む
    load_dotenv()
    
    # または特定のファイルを指定
    # load_dotenv('/path/to/.env')
    
    # 環境変数が設定されているか確認
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("⚠️ OPENROUTER_API_KEY not found in .env file")
        return None
    
    print(f"✅ API Key loaded from .env: {api_key[:10]}...")
    client = OpenRouterClient()
    return client


# 方法3: 設定ファイルから読み込む
def setup_from_config():
    """設定ファイルから読み込んで環境変数に設定"""
    config_path = Path.home() / '.config' / 'openrouter' / 'config.json'
    
    if config_path.exists():
        import json
        with open(config_path) as f:
            config = json.load(f)
            os.environ['OPENROUTER_API_KEY'] = config.get('api_key', '')
    
    return OpenRouterClient()


# 方法4: 複数の方法を試す（実用的）
def setup_api_key():
    """複数の方法で API キーを探す"""
    # 優先順位:
    # 1. 既に環境変数に設定されている
    if os.getenv('OPENROUTER_API_KEY'):
        print("✅ Using existing OPENROUTER_API_KEY environment variable")
        return OpenRouterClient()
    
    # 2. .env ファイルから読み込む
    if Path('.env').exists():
        load_dotenv()
        if os.getenv('OPENROUTER_API_KEY'):
            print("✅ Loaded API key from .env file")
            return OpenRouterClient()
    
    # 3. ユーザーの設定ディレクトリから
    config_file = Path.home() / '.openrouter_key'
    if config_file.exists():
        api_key = config_file.read_text().strip()
        os.environ['OPENROUTER_API_KEY'] = api_key
        print("✅ Loaded API key from ~/.openrouter_key")
        return OpenRouterClient()
    
    # 4. プロンプトで入力を求める
    print("⚠️ No API key found. Please enter your OpenRouter API key:")
    api_key = input("API Key: ").strip()
    if api_key:
        os.environ['OPENROUTER_API_KEY'] = api_key
        
        # オプション: 保存するか確認
        save = input("Save API key for future use? (y/N): ").lower()
        if save == 'y':
            config_file.write_text(api_key)
            print(f"✅ Saved to {config_file}")
        
        return OpenRouterClient()
    
    raise ValueError("No API key provided")


# サンプル: .env ファイルの作成
def create_env_template():
    """`.env.example` テンプレートを作成"""
    env_example = """# OpenRouter API Configuration
OPENROUTER_API_KEY=your-api-key-here

# Optional: Default model
OPENROUTER_DEFAULT_MODEL=google/gemini-2.0-flash-exp:free

# Optional: Timeout settings
OPENROUTER_TIMEOUT=30
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_example)
    
    print("✅ Created .env.example template")
    print("📝 Copy to .env and add your API key:")
    print("   cp .env.example .env")


if __name__ == "__main__":
    # 環境変数の設定方法デモ
    print("🦈 OpenRouter Environment Setup Demo\n")
    
    # .env.example を作成
    if not Path('.env.example').exists():
        create_env_template()
    
    # API キーをセットアップ
    try:
        client = setup_api_key()
        print("\n✅ Client initialized successfully!")
        
        # テスト
        response = client.simple_completion(
            "Say hello in one word",
            model="google/gemini-2.0-flash-exp:free"
        )
        print(f"Test response: {response}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")