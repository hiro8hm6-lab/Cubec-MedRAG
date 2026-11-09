import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError

# .env ファイルからAPIキーを読み込む
load_dotenv()

# Geminiクライアントの初期化
client = genai.Client()

# 解析したい論文のファイル名を指定（neuro.pdf, oncology.pdf, chest.pdf に変更済み）
pdf_path = "neuro.pdf"  # ← 他の論文を解析する場合はここを "oncology.pdf" や "chest.pdf" に書き換えます

print(f"'{pdf_path}' をアップロードしています...")
uploaded_file = client.files.upload(file=pdf_path)
print(f"アップロード完了: {uploaded_file.name}")

# サーバーエラー（500/503など）が起きたときに自動で最大3回まで再試行する仕組み
max_retries = 3
response = None

print("論文を解析し、詳細な分析を生成しています...")
for attempt in range(max_retries):
    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=[
                uploaded_file,
                "この論文について、以下の4点を医療従事者向けにわかりやすく構造化してまとめてください。\n"
                "1. 研究の背景と目的（何を解決しようとしているか）\n"
                "2. 使用されたモダリティ・データ・手法の特徴\n"
                "3. 主要な結果と精度（パフォーマンス評価）\n"
                "4. 臨床実装における課題や今後の展望（Limitations）"
            ]
        )
        break
    except ServerError as e:
        if attempt < max_retries - 1:
            print(f"サーバーで一時的なエラーが発生しました（試行 {attempt + 1}/{max_retries}）。5秒後に再試行します...")
            time.sleep(5)
        else:
            raise e

if response:
    print(f"\n--- {pdf_path} の解析結果 ---")
    print(response.text)