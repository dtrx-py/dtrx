[![GitHub](https://img.shields.io/badge/GitHub-dtrx--py/dtrx-8da0cb?style=for-the-badge&logo=github)](https://github.com/dtrx-py/dtrx)
[![PyPI
version](https://img.shields.io/pypi/v/dtrx.svg?style=for-the-badge&logo=PyPi&logoColor=white)](https://pypi.org/project/dtrx/)
[![PyPI
pyversions](https://img.shields.io/pypi/pyversions/dtrx.svg?style=for-the-badge&logo=python&logoColor=white&color=ff69b4)](https://pypi.python.org/pypi/dtrx/)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/dtrx-py/dtrx/main.yml?&branch=master&logo=github-actions&logoColor=white&style=for-the-badge)](https://github.com/dtrx-py/dtrx/actions?query=branch%3Amaster+)

<!-- toc -->

- [dtrx](#dtrx)
  - [Changes in this repo](#changes-in-this-repo)
  - [Development](#development)
    - [Contributions](#contributions)
    - [Issues](#issues)
    - [Running Tests](#running-tests)
    - [Releases](#releases)

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

## Development

### Contributions

Contributions are gladly welcomed! Feel free to open a Pull Request with any
changes.

### Issues

When posting an issue, it can be very handy to provide any example files (for
example, the archive that failed to extract) or reproduction steps so we can
address the problem quickly.

### Running Tests

The tests are most easily run from Docker. Check out the
[`Dockerfile`](Dockerfile) for how that's set up.

We push a pre-built image to Docker Hub as `dtrx-py/dtrx:latest`, so you can
pull that image and run the tests like so:

```bash
docker run --rm -it --volume $(pwd):/workspace ghcr.io/dtrx-py/dtrx:latest \
   bash -c "cp -r /workspace ~/scratch && cd ~/scratch && uv run -- tests/compare.py"
```

### Releases

Releases are tagged in this repo and published to pypi.org. The release process
for maintainers is the below steps:

1. update the version specifier:

   ```bash
   # update the version appropriately
   ❯ uv version X.Y.Z
   ❯ git add pyproject.toml uv.lock
   ❯ git commit  # fill in the commit message
   ```

2. create an annotated tag for the release.

   ```bash
   ❯ git tag -a {,-m}X.Y.Z
   ```

   be sure to push the tag, `git push --tags`.

3. use the `make publish-release` command to build and publish to GitHub and
   PyPi

See the [`Makefile`](Makefile) for details on what that rule does.
