import os
import time
from dotenv import load_dotenv
import fitz  # PyMuPDF: 高精度なPDFテキスト抽出ライブラリ
from google.genai.errors import ServerError
from llama_index.core import Document, Settings, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.google_genai import GoogleGenAI

# 環境変数の読み込み
load_dotenv()


def create_local_rag_engine(pdf_dir="PDF"):
  """PyMuPDFを使用してPDFから高精度にテキストを抽出し、

  LlamaIndexのベクトル検索エンジンを構築する
  """
  if not os.path.exists(pdf_dir) or not os.listdir(pdf_dir):
    raise FileNotFoundError(
        f"'{pdf_dir}' フォルダが見つからないか、PDFが含まれていません。"
    )

  print("🔄 ローカルEmbeddingモデルをロード中...")
  Settings.embed_model = HuggingFaceEmbedding(
      model_name="sentence-transformers/all-MiniLM-L6-v2"
  )

  # LLMとしてGeminiを設定
  Settings.llm = GoogleGenAI(model="gemini-3.8-flash")

  print(
      f"📚 '{pdf_dir}' フォルダからPyMuPDFでPDFのテキストを抽出・インデックス化中..."
  )

  documents = []
  # PDFフォルダ内の全ファイルを走査
  for file_name in os.listdir(pdf_dir):
    if file_name.endswith(".pdf"):
      pdf_path = os.path.join(pdf_dir, file_name)
      try:
        # PyMuPDFでPDFを開いて全ページのテキストを結合
        doc = fitz.open(pdf_path)
        full_text = ""
        for page_num in range(len(doc)):
          page = doc[page_num]
          full_text += page.get_text()

        if full_text.strip():
          # LlamaIndexのDocumentオブジェクトとして登録
          documents.append(
              Document(text=full_text, metadata={"file_name": file_name})
          )
          print(f"  - 読み込み成功: {file_name}")
        else:
          print(
              f"  - 警告: '{file_name}' からテキストが抽出できませんでした。"
          )
      except Exception as e:
        print(f"  - エラー ({file_name}): {e}")

  if not documents:
    raise ValueError("有効なテキストが抽出されたPDFがありません。")

  # ベクトルストアインデックスの構築
  index = VectorStoreIndex.from_documents(documents)

  # クエリエンジンの作成（類似度が高い上位のチャンクを根拠として抽出）
  query_engine = index.as_query_engine(similarity_top_k=3)

  print("✅ ローカルRAGエンジンの構築が完了しました！")
  return query_engine


if __name__ == "__main__":
  # 単体テスト実行用（自動リトライ機能付き）
  engine = create_local_rag_engine()

  query_text = (
      "各論文におけるAIモデルの精度と臨床的課題について教えてください。"
  )
  print(f"\n🔍 質問中: {query_text}")

  max_retries = 3
  response = None

  for attempt in range(max_retries):
    try:
      response = engine.query(query_text)
      break
    except ServerError as se:
      if attempt < max_retries - 1:
        print(
            f"サーバーが混雑しています（試行"
            f" {attempt + 1}/{max_retries})... 5秒後に再試行します。"
        )
        time.sleep(5)
      else:
        raise se

  print("\n--- ローカルRAGからの回答 ---")
  print(response)