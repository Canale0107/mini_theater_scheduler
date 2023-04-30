#!/bin/bash

# Dockerイメージ名とコンテナ名を指定
DOCKER_IMAGE=minitheater_scheduler_image
CONTAINER_NAME=minitheater_scheduler_container

# コンテナを作成して、マウントして、時刻も同期して、scheduler.pyを実行。シェルスクリプトのオプションをそのままオプションにする
# これで一応動くが、なんか遅いのと、文字が灰色にならない
docker run --rm -v "$(pwd)/../src:/workspace/src" -v /etc/localtime:/etc/localtime:ro -e PYTHONPATH=/workspace/src --name $CONTAINER_NAME $DOCKER_IMAGE:latest sh -c "cd src && python scheduler.py $@"