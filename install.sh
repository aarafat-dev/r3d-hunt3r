#!/bin/bash
set -e

RED='\033[0;31m'
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
DIM='\033[2m'
NC='\033[0m' # No Color

echo ""
echo -e "${RED}${BOLD}"
echo " ██████╗ ██████╗ ██████╗     ██╗  ██╗██╗   ██╗███╗   ██╗████████╗██████╗ ██████╗"
echo " ██╔══██╗╚════██╗██╔══██╗    ██║  ██║██║   ██║████╗  ██║╚══██╔══╝╚════██╗██╔══██╗"
echo " ██████╔╝ █████╔╝██║  ██║    ███████║██║   ██║██╔██╗ ██║   ██║    █████╔╝██████╔╝"
echo " ██╔══██╗ ╚═══██╗██║  ██║    ██╔══██║██║   ██║██║╚██╗██║   ██║    ╚═══██╗██╔══██╗"
echo " ██║  ██║██████╔╝██████╔╝    ██║  ██║╚██████╔╝██║ ╚████║   ██║   ██████╔╝██║  ██║"
echo " ╚═╝  ╚═╝╚═════╝ ╚═════╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═════╝ ╚═╝  ╚═╝"
echo -e "${NC}${DIM}   CTF AI Agent — SecDojo Edition  |  Powered by OpenRouter (Free Tier)${NC}"
echo ""

echo -e "${RED}[*]${NC} Starting installation..."
echo ""

# ── Check dependencies ──────────────────────────────────────────

echo -e "${RED}[*]${NC} Checking dependencies..."

if ! command -v python3 &>/dev/null; then
    echo -e "${RED}[!] python3 not found. Install it first:${NC}"
    echo "    sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

if ! command -v git &>/dev/null; then
    echo -e "${RED}[!] git not found. Installing...${NC}"
    sudo apt install -y git
fi

echo -e "${GREEN}[+]${NC} Dependencies OK"
echo ""

# ── Ask for install location ────────────────────────────────────

DEFAULT_DIR="$HOME/r3d-hunt3r"
echo -e "${BOLD}Where do you want to install R3D HUNT3R?${NC}"
echo -e "${DIM}Press Enter to use default: $DEFAULT_DIR${NC}"
read -rp "Install path: " INSTALL_DIR
INSTALL_DIR="${INSTALL_DIR:-$DEFAULT_DIR}"
echo ""

# ── Clone repo ──────────────────────────────────────────────────

REPO_URL="https://github.com/yourname/r3d-hunt3r.git"  # <-- update this

if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}[!] Directory $INSTALL_DIR already exists.${NC}"
    read -rp "    Overwrite? (y/N): " OVERWRITE
    if [[ "$OVERWRITE" =~ ^[Yy]$ ]]; then
        rm -rf "$INSTALL_DIR"
    else
        echo -e "${RED}[!] Installation cancelled.${NC}"
        exit 1
    fi
fi

echo -e "${RED}[*]${NC} Cloning repository..."
git clone "$REPO_URL" "$INSTALL_DIR"
cd "$INSTALL_DIR"
echo -e "${GREEN}[+]${NC} Repository cloned to $INSTALL_DIR"
echo ""

# ── Virtual environment ─────────────────────────────────────────

echo -e "${RED}[*]${NC} Setting up Python virtual environment..."
python3 -m venv .venv
source "$INSTALL_DIR/.venv/bin/activate"
pip install -e . -q
echo -e "${GREEN}[+]${NC} Virtual environment ready"
echo ""

# ── API Key ─────────────────────────────────────────────────────

echo -e "${BOLD}OpenRouter API Key Setup${NC}"
echo -e "${DIM}Get your FREE key at: https://openrouter.ai (no credit card required)${NC}"
echo -e "${DIM}50 free requests/day — flags are unique per instance so each member needs their own key${NC}"
echo ""

while true; do
    read -rsp "Enter your OpenRouter API key: " API_KEY
    echo ""
    if [[ -z "$API_KEY" ]]; then
        echo -e "${YELLOW}[!] No API key entered. You can set it later with:${NC}"
        echo "    export OPENROUTER_API_KEY=your_key_here"
        API_KEY=""
        break
    elif [[ ${#API_KEY} -lt 20 ]]; then
        echo -e "${YELLOW}[!] That key looks too short. Try again (or press Enter to skip).${NC}"
    else
        echo -e "${GREEN}[+]${NC} API key saved."
        break
    fi
done
echo ""

# ── Shell config ────────────────────────────────────────────────

echo -e "${RED}[*]${NC} Configuring shell..."

# Detect shell rc file
if [[ "$SHELL" == *zsh* ]]; then
    SHELL_RC="$HOME/.zshrc"
elif [[ "$SHELL" == *bash* ]]; then
    SHELL_RC="$HOME/.bashrc"
else
    SHELL_RC="$HOME/.bashrc"
fi

# Remove any old R3D HUNT3R entries
sed -i '/# R3D HUNT3R/,/^$/d' "$SHELL_RC" 2>/dev/null || true

# Append new config
cat >> "$SHELL_RC" << SHELLEOF

# R3D HUNT3R
source "$INSTALL_DIR/.venv/bin/activate"
SHELLEOF

if [[ -n "$API_KEY" ]]; then
cat >> "$SHELL_RC" << SHELLEOF
export OPENROUTER_API_KEY="$API_KEY"
SHELLEOF
fi

echo -e "${GREEN}[+]${NC} Shell config updated: $SHELL_RC"
echo ""

# ── Done ────────────────────────────────────────────────────────

echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════════╗"
echo -e "║        R3D HUNT3R installed successfully!    ║"
echo -e "╚══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${BOLD}To start using it:${NC}"
echo ""
echo -e "  1. Reload your shell:"
echo -e "     ${RED}source $SHELL_RC${NC}"
echo ""
echo -e "  2. Launch:"
echo -e "     ${RED}r3d-hunt3r${NC}"
echo ""
if [[ -z "$API_KEY" ]]; then
echo -e "  ${YELLOW}[!] Don't forget to set your API key:${NC}"
echo -e "     ${RED}export OPENROUTER_API_KEY=your_key_here${NC}"
echo ""
fi
echo -e "  ${DIM}Get a free OpenRouter key at: https://openrouter.ai${NC}"
echo ""
