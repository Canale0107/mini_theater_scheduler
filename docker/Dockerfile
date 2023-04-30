FROM python:3.9

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# ワーキングディレクトリを作成して設定
WORKDIR /workspace

# 必要なPythonパッケージをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# COPY makefile .