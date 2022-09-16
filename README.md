[![GitHub](https://img.shields.io/badge/GitHub-dtrx--py/dtrx-8da0cb?style=for-the-badge&logo=github)](https://github.com/dtrx-py/dtrx)
[![PyPI
version](https://img.shields.io/pypi/v/dtrx.svg?style=for-the-badge&logo=PyPi&logoColor=white)](https://pypi.org/project/dtrx/)
[![PyPI
pyversions](https://img.shields.io/pypi/pyversions/dtrx.svg?style=for-the-badge&logo=python&logoColor=white&color=ff69b4)](https://pypi.python.org/pypi/dtrx/)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/dtrx-py/dtrx/main-ci/master?logo=github-actions&logoColor=white&style=for-the-badge)](https://github.com/dtrx-py/dtrx/actions)

<!-- toc -->

- [dtrx](#dtrx)
  - [Changes in this repo](#changes-in-this-repo)
  - [Development](#development)
    - [Contributions](#contributions)
    - [Issues](#issues)
    - [Releases](#releases)
    - [Invoke + Tests](#invoke--tests)
    - [Linting](#linting)
    - [Docker](#docker)

<!-- tocstop -->

# dtrx

"**Do The Right eXtraction**" - don't remember what set of `tar` flags or where
to pipe the output to extract it? no worries!

TL;DR

```bash
pip install dtrx

dtrx yolo.tar.gz
```

This is a copy-paste of the original dtrx repo, and **all credit for this
software** should be attributed to the original author, Brett Smith @brettcs:

https://github.com/brettcs/dtrx

See the original [`README`](README) for more details on what this does!

## Changes in this repo

This repo contains some patches on top of the original source to enable using
`dtrx` with python3. The original motivation was to enable `dtrx` on Ubuntu
20.04+, where the `dtrx` apt package was removed from the default ppas (likely
due to being python2 only).

I attempted to get the tests all working via `tox` , for which I used a
Dockerfile to try to get some kind of environment consistency. You can run the
tests by running (requires Docker installed):

```bash
./test.sh
```

## Development

### Contributions

Contributions are gladly welcomed! Feel free to open a Pull Request with any
changes.

### Issues

When posting an issue, it can be very handy to provide any example files (for
example, the archive that failed to extract) or reproduction steps so we can
address the problem quickly.

### Releases

Releases are tagged in this repo and published to pypi.org. The release process
for maintainers is the below steps:

1. update the version specifier:

   ```bash
   # update the VERSION value in dtrx/dtrx.py, then:
   ❯ git add dtrx/dtrx.py
   ❯ git commit  # fill in the commit message
   ```

2. create an annotated tag for the release. usually good to put a list of new
   commits since the previous tag, for example by listing them with:

   ```bash
   ❯ git log $(git describe --tags --abbrev=0)..HEAD --oneline
   # create the annotated tag
   ❯ git tag -a <version number>
   ```

   be sure to push the tag, `git push --tags`.

3. use the `make publish-release` command to build and publish to GitHub and
   PyPi

See the [`Makefile`](Makefile) for details on what that rule does.

### Invoke + Tests

There's some minimal helper scripts for pyinvoke in [`tasks.py`](tasks.py).

To bootstrap, run `pip install -r requirements.txt`, then `inv --list` to see
available tasks:

```bash
❯ inv --list
Available tasks:

  build-docker                build docker image
  push-docker                 push docker image
  quick-test                  run quick tests in docker
  rst2man                     run rst2man in docker
  test-nonexistent-file-cmd   run test-nonexistent-file-cmd.sh
  tox                         run tox in docker
  windows                     just check that windows install fails. pulls a minimal wine docker image to test
```

To run the tests, run `inv tox`. Takes a couple of minutes to go through all the
python versions.

### Linting

Linting is provided by [pre-commit](pre-commit.com). To use it, first install
the pre-commit hook:

```bash
pip install pre-commit
pre-commit install
```

pre-commit will run anytime `git commit` runs (disable with `--no-verify`). You
can manually run it with `pre-commit run`.

### Docker

The tests in CI (and locally) can be run inside a Docker container, which
provides all the tested python versions.

This image is defined at [`Dockerfile`](Dockerfile). It's pushed to the GitHub
Container Registry so it can be managed by the `dtrx-py` organization on GitHub-
Docker Hub charges for Organizations.

There are Invoke tasks for building + pushing the Docker image, which push both
a `:latest` tag as well as a `:2022-09-16` ISO8601 numbered tag. The tag can
then be updated in the GitHub actions runner.

> Note: there's a bit of complexity around how the image is used, because the
> dtrx tests need to run as a non-root user (there's one test that checks for
> error handling when the output directory is not accessible by the current
> user). To deal with this, there's an entrypoint script that switches user to a
> non-root user, but that still has read/write access to the mounted host volume
> (which is the cwd, intended for local development work). This is required on
> Linux, where it's nice to have the host+container UID+GUID matching, so any
> changes to the mounted host volume have the same permissions set.
>
> In the GitHub actions runner, we need to run inside the same container (to
> have access to the correct python versions for testing), and the github action
> for checkout assumes it can write to somewhat arbitrary locations in the file
> system (basically root access). So we switch to the non-root user _after_
> checkout.
