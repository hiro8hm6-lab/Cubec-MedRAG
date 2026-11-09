# 軽量で安全なPython公式イメージをベースにする
FROM python:3.11-slim

# 作業ディレクトリの設定
WORKDIR /app

# システム依存パッケージのインストール（PyMuPDFやビルドに必要な最小限のツール）
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 依存関係ファイルを先にコピーしてキャッシュを活用
COPY requirements.txt .

# Pythonパッケージのインストール
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# アプリケーションの全ファイルをコンテナ内にコピー
COPY . .

# Streamlitのデフォルトポートを公開
EXPOSE 8501

# コンテナ起動時にStreamlitアプリを実行するコマンド
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]