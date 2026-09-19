#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
python scripts/generate_test_workbooks.py
destination="${1:-output/demo-$(date +%Y%m%d-%H%M%S)}"
data-maturity analyze tests/fixtures/dirty_customers.xlsx --no-llm --output "$destination"
printf 'Reports: %s\n' "$destination"
