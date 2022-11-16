"""
Invoke docker tasks
"""

import os
import shutil
import sys
from datetime import date

import invoke

from . import utils

DOCKER_IMAGE_NAME = "ghcr.io/dtrx-py/dtrx"


def in_docker():
    """check if we are in a docker container"""
    return os.path.exists("/.dockerenv")


@invoke.task
def build(ctx):
    """build docker image"""
    if in_docker():
        # already in a docker container, probably
        return

    # Make sure we have the docker utility
    if not shutil.which("docker"):
        print("🐋 Please install docker first 🐋")
        sys.exit(1)

    # build the docker image
    with ctx.cd(utils.ROOT_DIR):
        ctx.run(
            f'docker build -t "{DOCKER_IMAGE_NAME}:{date.today().isoformat()}" -t'
            f' "{DOCKER_IMAGE_NAME}:latest" .',
            env={"DOCKER_BUILDKIT": "1"},
            pty=True,
        )


@invoke.task(pre=[build])
def push(ctx):
    """push docker image"""
    ctx.run(f"docker push {DOCKER_IMAGE_NAME}:latest", pty=True)
    ctx.run(f"docker push {DOCKER_IMAGE_NAME}:{date.today().isoformat()}", pty=True)


def run_in_docker(ctx, cmd):
    """run cmd. if in docker already, just run it. if not, run it in docker"""
    if in_docker():
        ctx.run(cmd, pty=True)
    else:
        ctx.run(
            f"docker run --rm -it -v {utils.ROOT_DIR}:/app -w /app"
            f" {DOCKER_IMAGE_NAME} {cmd}",
            pty=True,
        )


collection = invoke.Collection(
    "docker",
    build,
    push,
)
