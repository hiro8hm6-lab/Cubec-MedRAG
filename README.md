# Cubec-MedRAG

弘前大学医学部での臨床・研究の知見を活かし、膨大な医療論文やPDFから正確に知見を抽出・クロス分析するために開発した、マルチモーダル医療研究論文RAG（Retrieval-Augmented Generation）システムです。

## 🚀 主な機能・特徴
- **マルチモーダル論文解析**: 医学論文PDF（放射線科・画像診断や臨床研究等）を読み込み、高度なセマンティック検索と情報抽出を実行。
- **ローカル＆クラウドのハイブリッド構成**: 安定した処理とプライバシー配慮を両立させるためのローカル埋め込み・検索バックエンドとAPIの統合。
- **Docker対応**: 環境構築の属人性を排し、コンテナ技術によってどこでもワンコマンドで再現・デプロイ可能な設計。
- **評価・精度検証モジュール**: RAGの出力精度を定量的に評価・検証する仕組み（`rag_evaluator.py`）を実装。

## 🛠️ 技術スタック
- **言語**: Python 3.13
- **AI / RAG**: LlamaIndex, HuggingFace Embeddings, Gemini API
- **UI / インフラ**: Streamlit, Docker / Docker Compose
- **PDF処理**: PyMuPDF (`fitz`)

## 📂 ディレクトリ構成
- `app.py`: StreamlitによるメインUIおよびアプリケーション制御
- `rag_backend.py` / `rag_pdf_reader.py`: PDFの読み込み・前処理およびRAGバックエンド処理
- `analyze_papers.py` / `multi_paper_analyzer.py`: 複数論文のクロス分析・評価ロジック
- `Dockerfile` / `.dockerignore`: コンテナ化のための設定ファイル
