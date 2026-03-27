#!/usr/bin/env bash
set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

say() { echo -e "${GREEN}[labeldesk]${NC} $1"; }
warn() { echo -e "${YELLOW}[labeldesk]${NC} $1"; }
die() { echo -e "${RED}[labeldesk]${NC} $1"; exit 1; }

say "setting up labeldesk..."

# check python
if ! command -v python3 &>/dev/null; then
  die "python3 not found - install python 3.13+"
fi
PYVER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
say "python $PYVER detected"

# install uv if missing
if ! command -v uv &>/dev/null; then
  say "installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
  command -v uv &>/dev/null || die "uv install failed - add ~/.local/bin to PATH"
fi

# sync deps
say "syncing deps..."
uv sync --extra dev

# optional: ai extras
read -p "$(echo -e "${YELLOW}install ai sdks (anthropic/openai/gemini)? [y/N]${NC} ")" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  uv sync --extra ai
fi

# seed config if missing
if [[ ! -f labeldesk.yaml && ! -f "$HOME/.labeldesk/config.yaml" ]]; then
  say "creating labeldesk.yaml from example..."
  cp labeldesk.yaml.example labeldesk.yaml
  warn "edit labeldesk.yaml to add api keys"
fi

# tesseract check
if ! command -v tesseract &>/dev/null; then
  warn "tesseract not found - ocr path disabled"
  warn "  debian/ubuntu: sudo apt install tesseract-ocr"
  warn "  arch:          sudo pacman -S tesseract"
  warn "  macos:         brew install tesseract"
fi

# run tests
say "running tests..."
uv run pytest tests/ -q || die "tests failed"

say "done!"
echo
echo "  run tui:        uv run labeldesk"
echo "  run web:        uv run labeldesk --web"
echo "  label imgs:     uv run labeldesk label ./path/to/imgs"
echo "  docker:         docker compose up"
echo

# launch
read -p "$(echo -e "${YELLOW}start now? [T]ui / [W]eb / [N]o ${NC}")" -n 1 -r
echo
case $REPLY in
  [Tt]) exec uv run labeldesk ;;
  [Ww]) exec uv run labeldesk --web ;;
  *) say "bye" ;;
esac
