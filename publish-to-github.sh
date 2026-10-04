#!/usr/bin/env bash
set -euo pipefail

REPO_NAME="${1:-fusion360-linux-arch-fixes}"
VISIBILITY="${2:-public}"

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is required." >&2
  echo "Arch: sudo pacman -S github-cli" >&2
  exit 1
fi

gh auth status

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git init
  git add .
  git commit -m "Initial Arch/CachyOS Fusion 360 fixes"
fi

case "$VISIBILITY" in
  public|private) ;;
  *) echo "Visibility must be public or private" >&2; exit 2 ;;
esac

if git remote get-url origin >/dev/null 2>&1; then
  echo "origin already exists: $(git remote get-url origin)"
  git push -u origin HEAD
else
  gh repo create "$REPO_NAME" "--$VISIBILITY" \
    --description "Unofficial Arch/CachyOS compatibility fixes for stonegray/fusion360-linux" \
    --source=. --remote=origin --push
fi

echo "Published: $(git remote get-url origin)"
