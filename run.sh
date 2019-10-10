#!/bin/bash -e

DOCKER_IMAGE_NAME="jackwzh/acestream-server"
SERVER_HTTP_PORT="6878"

docker run \
	--name ace-server \
	--publish "$SERVER_HTTP_PORT:$SERVER_HTTP_PORT" \
	-p 8621:8621 \
	--rm \
	--mount type=tmpfs,target=/dev/disk/by-id,tmpfs-mode=660,tmpfs-size=4k \
	--mount type=tmpfs,target=/root/.ACEStream,tmpfs-mode=660,tmpfs-size=8192m \
	"$DOCKER_IMAGE_NAME"
