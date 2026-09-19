#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
ruff check .
mypy src
pytest --cov=data_maturity --cov-report=term-missing
