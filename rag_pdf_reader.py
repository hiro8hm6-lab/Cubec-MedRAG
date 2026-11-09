import os
from dotenv import load_dotenv
from google import genai

# .env ファイルからAPIキーを読み込む
load_dotenv()

# Geminiクライアントの初期化
client = genai.Client()

# 1. 準備したPDFファイルをGeminiのファイルAPIにアップロードする
pdf_path = "sample_medical.pdf"  # ←お手元のPDFファイル名に変更してください

print(f"'{pdf_path}' をアップロードしています...")
uploaded_file = client.files.upload(file=pdf_path)
print(f"アップロード完了: {uploaded_file.name}")

# 2. アップロードしたPDFをコンテキストにして質問を投げる
print("\nPDFの内容を解析し、質問に対する回答を生成しています...")
response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents=[
        uploaded_file,
        "この文書の主要なポイントを3つにまとめて、医療従事者向けにわかりやすく解説してください。"
    ]
)

print("\n--- PDFに基づくAIからの回答 ---")
print(response.text)