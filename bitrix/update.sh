#!/usr/bin/env bash
# update.sh — Update the Bitrix Claude Code skill
# Run: bash ~/.claude/skills/bitrix/update.sh [--force]
set -euo pipefail

REPO="Poliklot/claude-bitrix-skill"
BRANCH="master"
INSTALL_SCRIPT_URL="https://raw.githubusercontent.com/${REPO}/${BRANCH}/install.sh"

echo "Fetching latest installer from GitHub..."
SCRIPT=$(curl -fsSL --retry 3 --retry-delay 2 "$INSTALL_SCRIPT_URL")
[[ -z "$SCRIPT" ]] && { echo "Error: Could not download install.sh" >&2; exit 1; }
exec bash -c "$SCRIPT" -- "$@"
