import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError

# .env ファイルからAPIキーを読み込む
load_dotenv()

# Geminiクライアントの初期化
client = genai.Client()

# まとめて解析したい3つの論文ファイル
pdf_paths = ["neuro.pdf", "oncology.pdf", "chest.pdf"]
uploaded_files = []

print("3つの論文ファイルをアップロードしています...")
for path in pdf_paths:
    if not os.path.exists(path):
        print(f"エラー: '{path}' が見つかりません。ファイル名を確認してください。")
        exit()
    print(f"  - アップロード中: {path}")
    file_obj = client.files.upload(file=path)
    uploaded_files.append(file_obj)
print("すべてのファイルのアップロードが完了しました！\n")

# サーバーエラー対策のリトライ設定
max_retries = 3
response = None

print("3つの論文を横断的に比較・分析しています（これには少し時間がかかります）...")
for attempt in range(max_retries):
    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=[
                *uploaded_files,  # 3つのファイルをまとめて渡す
                "これら3つの医療・放射線分野の論文（神経画像、放射線治療、AI診断支援）を横断的に分析し、"
                "医療従事者の視点から以下の4項目について比較・構造化してまとめてください。\n\n"
                "1. 各論文の主要テーマと解決しようとしている臨床課題の比較\n"
                "2. 使用されたモダリティやデータ（規模・特性）の違い\n"
                "3. AIモデルの性能・評価結果における共通点と相違点\n"
                "4. 臨床実装（Clinical Implementation）に向けた共通の障壁や今後の課題\n\n"
                "※注意: Markdownの表（テーブル）のセル内では、<br>などのHTMLタグを使用せず、スペースや通常のテキストで記述してください。"
            ]
        )
        break
    except ServerError as e:
        if attempt < max_retries - 1:
            print(f"サーバーが混雑しています（試行 {attempt + 1}/{max_retries}). 5秒後に再試行します...")
            time.sleep(5)
        else:
            raise e

if response:
    print("\n--- 3論文の横断比較・分析結果 ---")
    
    # 【修正箇所】レスポンス内の <br> タグを半角スペースに置換してから出力する
    cleaned_text = response.text.replace("<br>", " ")
    print(cleaned_text)