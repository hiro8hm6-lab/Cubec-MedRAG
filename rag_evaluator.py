import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError

# .env ファイルからAPIキーを読み込む
load_dotenv()

# Geminiクライアントの初期化
client = genai.Client()

print("AIに接続しています...")

# 503エラー（混雑）のときに自動で最大5回までやり直す仕組み
max_retries = 5
response = None

for attempt in range(max_retries):
    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents="医学・医療分野のRAGシステム構築において、LlamaIndexとGeminiを使うメリットを簡潔に3つ教えてください。"
        )
        break
    except ServerError as e:
        if attempt < max_retries - 1:
            print(f"サーバーが混雑しています（試行 {attempt + 1}/{max_retries}）。少し待って再試行します...")
            time.sleep(5) # 5秒待機
        else:
            raise e

if response:
    print("\n--- AIからの回答 ---")
    print(response.text)