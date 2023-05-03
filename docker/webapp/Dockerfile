# ベースとなるイメージの指定
FROM python:3.8-slim-buster

# コンテナ内での作業ディレクトリの指定
WORKDIR /app

# 必要なPythonライブラリをインストールする
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ポート番号の指定
EXPOSE 3333