#!/usr/bin/env bash
# One-command demo run. Stdlib only — no installs needed.
set -e
cd "$(dirname "$0")"
python3 pipeline.py "$@"
