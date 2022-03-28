#!/usr/bin/env bash
# Small script to run rst2man.py and error if there's any output
set -e

# rst2man.py doesn't return non-zero on warnings or errors 🤦
# instead, if it outputs anything on stdout or stderr, assume it's some abnormal
# result and error
output="$(rst2man.py "$1" "$2"  2>&1)"

if [ -n "$output" ]; then
    echo "$output" && false;
fi
