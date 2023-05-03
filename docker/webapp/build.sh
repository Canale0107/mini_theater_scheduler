#!/bin/bash

# Dockerイメージ名を指定
DOCKER_IMAGE=minitheater_webapp_image

# Dockerfileからイメージをビルドする
docker build -t $DOCKER_IMAGE .
