#!/usr/bin/env bash

# Simple test script to run the tests in docker

# Error on any non-zero command, and print the commands as they're run
set -ex

# Make sure we have the docker utility
if ! command -v docker; then
    echo "🐋 Please install docker first 🐋"
    exit 1
fi

# Set the docker image name to default to repo basename
DOCKER_IMAGE_NAME=${DOCKER_IMAGE_NAME:-$(basename -s .git "$(git remote --verbose | awk 'NR==1 { print tolower($2) }')")}

# build the docker image
DOCKER_BUILDKIT=1 docker build -t "$DOCKER_IMAGE_NAME" --build-arg "UID=$(id -u)" -f Dockerfile .

# by default, run tox
RUN_JOB=${RUN_JOB:-tox}

case $RUN_JOB in
    tox)
        # execute tox in the docker container. don't run in parallel; conda has
        # issues when we do this (pkg cache operations are not atomic!)
        docker run -v "$(pwd)":/mnt/workspace -t "$DOCKER_IMAGE_NAME" bash -c "tox $TOX_ARGS"
    ;;
    rst2man)
        # build man page from README
        docker run -v "$(pwd)":/mnt/workspace -t "$DOCKER_IMAGE_NAME" bash gen-manpage.sh README dtrx.1
    ;;
esac
