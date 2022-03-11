#!/usr/bin/env bash

set -ex

# Run a quick test in a docker image that doesn't have the 'file' command
# installed, and check for any unhandled tracebacks in the output.
docker run --rm -t --volume "$PWD:/workdir" python:3.10-slim-buster@sha256:ae30f2166f4389e553b642af9f22f7d17ba7fe584e0dd8bf9c75c36d836aabc3 /bin/bash -c "
cd /workdir && pip install . && touch /tmp/yolo.zip && cd /tmp && dtrx yolo.zip 2>&1 | tee /dev/stderr | ( ! grep 'Traceback (most recent call last):')
"
