#!/usr/bin/env bash

set -e

# Simple check that installing on windows fails as expected.
uv build --no-build-logs
docker run --rm -v "$(pwd)":/workdir -t tobix/pywine:3.10 bash -c 'wine pip install /workdir/dist/*.whl' \
  | tee /dev/stderr \
  | grep -q 'UnsupportedPython: One or more packages do not support'

echo '✅ Windows installation test passed: installation failed as expected!'
