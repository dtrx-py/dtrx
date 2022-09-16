import os
import shutil
import sys
from datetime import date

import invoke

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCKER_IMAGE_NAME = "ghcr.io/dtrx-py/dtrx"


def in_docker():
    return os.path.exists("/.dockerenv")


@invoke.task
def build_docker(ctx):
    """build docker image"""
    if in_docker():
        # already in a docker container, probably
        return

    # Make sure we have the docker utility
    if not shutil.which("docker"):
        print("🐋 Please install docker first 🐋")
        sys.exit(1)

    # build the docker image
    with ctx.cd(ROOT_DIR):
        ctx.run(
            f'docker build -t "{DOCKER_IMAGE_NAME}:{date.today().isoformat()}" -t'
            f' "{DOCKER_IMAGE_NAME}:latest" .',
            env={"DOCKER_BUILDKIT": "1"},
            pty=True,
        )


@invoke.task(pre=[build_docker])
def push_docker(ctx):
    """push docker image"""
    ctx.run(f"docker push {DOCKER_IMAGE_NAME}:latest", pty=True)
    ctx.run(f"docker push {DOCKER_IMAGE_NAME}:{date.today().isoformat()}", pty=True)


def run_in_docker(ctx, cmd):
    """run cmd. if in docker already, just run it. if not, run it in docker"""
    if in_docker():
        ctx.run(cmd, pty=True)
    else:
        ctx.run(
            f"docker run --rm -it -v {ROOT_DIR}:/app -w /app {DOCKER_IMAGE_NAME} {cmd}",
            pty=True,
        )


@invoke.task(pre=[build_docker])
def tox(ctx):
    """run tox in docker"""
    run_in_docker(ctx, "tox --tox-pyenv-no-fallback $TOX_ARGS")


@invoke.task(pre=[build_docker])
def quick_test(ctx):
    """run quick tests in docker"""
    run_in_docker(ctx, "python3 tests/compare.py")


@invoke.task(pre=[build_docker])
def rst2man(ctx):
    """run rst2man in docker"""
    run_in_docker(ctx, "bash tools/gen-manpage.sh archived/README dtrx.1")


@invoke.task
def test_nonexistent_file_cmd(ctx):
    """run test-nonexistent-file-cmd.sh"""
    if in_docker():
        print("error: this should not be run in docker!")
        sys.exit(1)
    ctx.run("./tools/test-nonexistent-file-cmd.sh")


@invoke.task
def windows(ctx):
    """just check that windows install fails. pulls a minimal wine docker image to test"""
    if in_docker():
        print("error: this should not be run in docker!")
        sys.exit(1)
    ctx.run(
        'docker run --rm -v "$(pwd)":/workdir -t tobix/pywine:3.9 bash -c \'wine pip'
        " install /workdir' | tee /dev/stderr | grep -q 'ERROR: No matching"
        " distribution found for platform==unsupported' || echo \"ERROR: pip install"
        ' should fail!"',
        pty=True,
    )
