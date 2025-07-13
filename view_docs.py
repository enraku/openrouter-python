#!/usr/bin/env python3
"""
OpenRouter Documentation Viewer
簡単にドキュメントをビルド・表示するためのツール
"""
import os
import subprocess
import webbrowser
import http.server
import socketserver
import threading
from pathlib import Path


def build_docs():
    """Sphinxドキュメントをビルド"""
    print("📚 Building documentation...")
    docs_dir = Path(__file__).parent / "docs"
    
    # uvコマンドでビルド
    result = subprocess.run(
        ["uv", "run", "make", "html"],
        cwd=docs_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Documentation built successfully!")
        return True
    else:
        print(f"❌ Build failed: {result.stderr}")
        return False


def serve_docs(port=8000):
    """ローカルサーバーでドキュメントを提供"""
    html_dir = Path(__file__).parent / "docs" / "_build" / "html"
    
    if not html_dir.exists():
        print("❌ Documentation not found. Building first...")
        if not build_docs():
            return
    
    os.chdir(html_dir)
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            # ログを抑制
            pass
    
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"🌐 Serving documentation at http://localhost:{port}")
        print("📋 Press Ctrl+C to stop the server")
        
        # ブラウザで開く
        webbrowser.open(f"http://localhost:{port}")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")


def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenRouter Documentation Viewer")
    parser.add_argument("--build-only", action="store_true", help="Build docs without serving")
    parser.add_argument("--port", type=int, default=8000, help="Port for local server (default: 8000)")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser automatically")
    
    args = parser.parse_args()
    
    if args.build_only:
        build_docs()
    else:
        # ブラウザ自動起動の設定
        if args.no_browser:
            global webbrowser
            webbrowser = type('DummyBrowser', (), {'open': lambda x: None})()
        
        serve_docs(args.port)


if __name__ == "__main__":
    main()