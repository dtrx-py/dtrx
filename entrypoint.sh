#!/usr/bin/env bash

# Attempt to detect the host UID + GUID, and create a matching user, and run any
# commands passed (or bash if none).

# This is useful to use a Docker image without modification that can read/write
# to a hosted volume as the same UID + GUID as the host.

# This script inspired by:
# https://www.joyfulbikeshedding.com/blog/2021-03-15-docker-and-the-host-filesystem-owner-matching-problem.html

set -e

USERNAME=builder

HOST_DIR=${PWD}

HOST_UID=$(stat -c "%u" "$HOST_DIR")
HOST_GID=$(stat -c "%g" "$HOST_DIR")

# Use this code if you want to modify an existing user account:
groupmod --gid "$HOST_GID" ${USERNAME}
usermod --uid "$HOST_UID" ${USERNAME}

# Drop privileges and execute next container command, or 'bash' if not specified.
if [[ $# -gt 0 ]]; then
    exec sudo -u ${USERNAME} -H PATH="${PATH}" PYENV_ROOT="${PYENV_ROOT}" -- "$@"
else
    exec sudo -u ${USERNAME} -H PATH="${PATH}" PYENV_ROOT="${PYENV_ROOT}" -- bash
fi
