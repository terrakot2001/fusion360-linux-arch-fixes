#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ $EUID -eq 0 ]]; then
  echo "Do not run this installer as root. Run it as your normal desktop user." >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  if command -v pacman >/dev/null 2>&1; then
    echo "python3 is required; installing it with pacman..."
    sudo pacman -S --needed --noconfirm python
  else
    echo "python3 is required and could not be installed automatically." >&2
    exit 2
  fi
fi

exec python3 "$ROOT/fusion360_bootstrap.py" "$@"
