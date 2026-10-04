#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/terrakot2001/fusion360-linux-arch-fixes.git"
REF="${FUSION_ARCH_FIXES_REF:-main}"

if [[ $EUID -eq 0 ]]; then
  echo "Do not run this installer as root. Run it as your normal desktop user." >&2
  exit 1
fi

if [[ ! -r /etc/os-release ]]; then
  echo "Cannot identify the Linux distribution." >&2
  exit 1
fi

# shellcheck disable=SC1091
source /etc/os-release
id_lower="${ID,,}"
id_like_lower="${ID_LIKE:-}"
id_like_lower="${id_like_lower,,}"
case " $id_lower $id_like_lower " in
  *" arch "*|*" cachyos "*|*" manjaro "*|*" endeavouros "*|*" garuda "*|*" artix "*) ;;
  *)
    echo "This quick installer is for Arch-family distributions only." >&2
    echo "Detected: ${PRETTY_NAME:-$ID}" >&2
    exit 2
    ;;
esac

if ! command -v git >/dev/null 2>&1; then
  echo "Installing git..."
  sudo pacman -S --needed --noconfirm git
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "Installing Python..."
  sudo pacman -S --needed --noconfirm python
fi

tmp="$(mktemp -d -t fusion360-arch-fixes.XXXXXX)"
cleanup() {
  rm -rf "$tmp"
}
trap cleanup EXIT

git clone --depth 1 --branch "$REF" "$REPO_URL" "$tmp/repo"
cd "$tmp/repo"
bash install.sh "$@"
