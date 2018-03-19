#!/bin/sh
set -eu

readonly PROJECT_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")

IMAGE_SHA=$(docker build -q $PROJECT_DIR/docker)
docker run --volume "$PROJECT_DIR:/tmp/project" -it --rm $IMAGE_SHA sh
docker rmi $IMAGE_SHA