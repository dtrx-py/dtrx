"""
Invoke top-level tasks entrance point.
"""

import sys

import invoke

from . import docker, utils


@invoke.task(pre=[docker.build])
def tox(ctx):
    """run tox in docker"""
    docker.run_in_docker(ctx, "tox --tox-pyenv-no-fallback $TOX_ARGS")


@invoke.task(pre=[docker.build])
def quick_test(ctx):
    """run quick tests in docker"""
    docker.run_in_docker(ctx, "python3 tests/compare.py")


@invoke.task(pre=[docker.build])
def rst2man(ctx):
    """run rst2man in docker"""
    docker.run_in_docker(ctx, "bash tools/gen-manpage.sh archived/README dtrx.1")


@invoke.task
def test_nonexistent_file_cmd(ctx):
    """run test-nonexistent-file-cmd.sh"""
    if docker.in_docker():
        print("error: this should not be run in docker!")
        sys.exit(1)
    with ctx.cd(utils.ROOT_DIR):
        ctx.run("./tools/test-nonexistent-file-cmd.sh")


@invoke.task
def windows(ctx):
    """
    just check that windows install fails. pulls a minimal wine docker image to test
    """
    if docker.in_docker():
        print("error: this should not be run in docker!")
        sys.exit(1)
    ctx.run(
        (
            'docker run --rm -v "$(pwd)":/workdir -t tobix/pywine:3.9 bash -c \'wine'
            " pip install /workdir' | tee /dev/stderr | grep -q 'UnsupportedPython: One"
            " or more packages do not support'"
        ),
        pty=True,
    )

    print("Hooray 🎉! Windows install failed as expected.")


# Top-level tasks
namespace = invoke.Collection(
    tox, quick_test, rst2man, test_nonexistent_file_cmd, windows
)
# Subtasks
namespace.add_collection(docker.collection)
