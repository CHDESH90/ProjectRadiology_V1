#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! python3 -m venv /tmp/cursor-venv-probe >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends python3-venv
fi
rm -rf /tmp/cursor-venv-probe

VENV="$ROOT/.venv"
if [[ ! -d "$VENV" ]]; then
  python3 -m venv "$VENV"
fi

# shellcheck disable=SC1091
source "$VENV/bin/activate"

python -m pip install --quiet --upgrade pip wheel
if [[ -f requirements.txt ]]; then
  python -m pip install --quiet -r requirements.txt
fi

echo "Install complete: $(python --version), venv at $VENV"
