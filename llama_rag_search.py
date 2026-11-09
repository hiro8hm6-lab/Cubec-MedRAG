import os
import time
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# .env ファイルからAPIキーを読み込む
load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key

print("LLMにGoogle GenAI、埋め込みモデルにローカルを設定しています...")

# 1. LLMの設定
llm = GoogleGenAI(model="gemini-3.8-flash", temperature=0.1)

# 2. ローカル埋め込みの設定
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

Settings.llm = llm
Settings.embed_model = embed_model

# プロジェクトフォルダ内にある指定の3つのPDFファイルだけを明示的に読み込む
target_files = ["neuro.pdf", "oncology.pdf", "chest.pdf"]
print("PDF文書を読み込んでいます...")

documents = []
for file_name in target_files:
    if os.path.exists(file_name):
        reader = SimpleDirectoryReader(input_files=[file_name])
        docs = reader.load_data()
        print(f"  - {file_name}: {len(docs)} ページを読み込みました")
        documents.extend(docs)
    else:
        print(f"  - 警告: '{file_name}' が見つかりません。")

print(f"合計文書数: {len(documents)} ページ\n")

if len(documents) == 0:
    print("エラー: 読み込めるPDF文書がありません。ファイル名を確認してください。")
    exit()

# ベクトルインデックスの構築
print("ベクトルインデックスを構築中...")
index = VectorStoreIndex.from_documents(
    documents,
    embed_model=embed_model,
    llm=llm
)

query_engine = index.as_query_engine(similarity_top_k=3, llm=llm)

query_text = "3つの論文のうち、胸部X線やCTにおけるAI診断支援や自動輪郭描画（Auto-contouring）の臨床的課題や限界について比較して教えてください。"

print(f"\n【質問】: {query_text}\n")
print("関連する論文の箇所を検索し、回答を生成しています...")

# 503エラー対策のリトライループ
max_retries = 3
response = None

for attempt in range(max_retries):
    try:
        response = query_engine.query(query_text)
        break
    except Exception as e:
        if "503" in str(e) or "UNAVAILABLE" in str(e):
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                print(f"サーバーが混雑しています（試行 {attempt + 1}/{max_retries}）。{wait_time}秒後に再試行します...")
                time.sleep(wait_time)
            else:
                raise e
        else:
            raise e

if response:
    print("\n--- RAGシステムからの回答 ---")
    print(response)