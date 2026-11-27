#!/usr/bin/env bash
# Format and lint Python files with the house style in ../ruff.toml.
#
# Usage: format.sh [--check] PATH...
#   --check   report problems without changing files (exit 1 if any)
#   PATH      files or folders to process (required; never defaults to the whole repo)
set -euo pipefail

RUFF_VERSION="0.16.9"
CONFIG="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/ruff.toml"
RUFF=(uvx --quiet "ruff@${RUFF_VERSION}")

check=false
if [[ "${1:-}" == "--check" ]]; then
    check=true
    shift
fi
if [[ $# -eq 0 ]]; then
    echo "usage: format.sh [--check] PATH..." >&2
    exit 2
fi

if $check; then
    status=0
    "${RUFF[@]}" format --config "$CONFIG" --check --diff "$@" || status=1
    "${RUFF[@]}" check --config "$CONFIG" "$@" || status=1
    exit $status
fi

# Fix first (sorts imports, removes unused ones), then format, then report what remains.
"${RUFF[@]}" check --config "$CONFIG" --fix --exit-zero --quiet "$@"
"${RUFF[@]}" format --config "$CONFIG" "$@"
"${RUFF[@]}" check --config "$CONFIG" "$@"
