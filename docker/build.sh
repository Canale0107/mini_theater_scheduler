#!/bin/bash

# Dockerイメージ名を指定
DOCKER_IMAGE=minitheater_scheduler_image

# Dockerfileからイメージをビルドする
docker build -t $DOCKER_IMAGE .
echo "イメージをビルドしました."
