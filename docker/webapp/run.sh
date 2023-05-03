#!/bin/bash

# Dockerイメージ名とコンテナ名を指定
DOCKER_IMAGE=minitheater_webapp_image
CONTAINER_NAME=minitheater_webapp_container

# コンテナを作成して、マウントして、時刻も同期して、scheduler.pyを実行。シェルスクリプトのオプションをそのままオプションにする
# TODO: ディレクトリ構成を見直してもっといい書き方をする
# TODO: volumeはdocker-composeに書く
# TODO: srcの中のtheater_settings.pyのみ参照する必要がある。この設定ファイルのパスは後々変えよう。
docker run --rm -v "$(pwd)/../../src:/app/src" -v "$(pwd)/../../data:/app/data" -v /etc/localtime:/etc/localtime:ro -p 3333:3333 --name $CONTAINER_NAME $DOCKER_IMAGE:latest sh -c "cd src/webapp && python app.py"