#!/bin/bash -e

DIRNAME=$(dirname "$0")
DOCKER_IMAGE_NAME="jackwzh/acestream-server"

docker build \
	--tag "$DOCKER_IMAGE_NAME" \
	--force-rm \
	"$DIRNAME"
