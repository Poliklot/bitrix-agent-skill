#!/usr/bin/env bash
# install.sh — Install or update the Bitrix Claude Code skill
# Usage: bash install.sh [--force]
set -euo pipefail

REPO="Poliklot/claude-bitrix-skill"
BRANCH="master"
INSTALL_DIR="${HOME}/.claude/skills/bitrix"
REMOTE_VERSION_URL="https://raw.githubusercontent.com/${REPO}/${BRANCH}/bitrix/VERSION"
TARBALL_URL="https://github.com/${REPO}/archive/refs/heads/${BRANCH}.tar.gz"

FORCE=false
[[ "${1:-}" == "--force" ]] && FORCE=true

print_step()  { printf "\n\033[1;34m==>\033[0m %s\n" "$1"; }
print_ok()    { printf "  \033[1;32m✓\033[0m %s\n" "$1"; }
print_warn()  { printf "  \033[1;33m!\033[0m %s\n" "$1"; }
print_error() { printf "\n\033[1;31mError:\033[0m %s\n" "$1" >&2; }

for cmd in curl tar; do
  command -v "$cmd" &>/dev/null || { print_error "'$cmd' is required but not installed."; exit 1; }
done

print_step "Checking versions"

REMOTE_VERSION=$(curl -fsSL "$REMOTE_VERSION_URL" 2>/dev/null | tr -d '[:space:]')
[[ -z "$REMOTE_VERSION" ]] && { print_error "Could not fetch remote version."; exit 1; }
print_ok "Remote version: ${REMOTE_VERSION}"

LOCAL_VERSION_FILE="${INSTALL_DIR}/VERSION"
if [[ -f "$LOCAL_VERSION_FILE" ]]; then
  LOCAL_VERSION=$(tr -d '[:space:]' < "$LOCAL_VERSION_FILE")
  print_ok "Installed version: ${LOCAL_VERSION}"
else
  LOCAL_VERSION=""
  print_warn "No installed version found."
fi

if [[ "$FORCE" == false && "$LOCAL_VERSION" == "$REMOTE_VERSION" ]]; then
  printf "\n\033[1;32mAlready up to date.\033[0m (%s)\n" "$REMOTE_VERSION"
  exit 0
fi

[[ -n "$LOCAL_VERSION" && "$LOCAL_VERSION" != "$REMOTE_VERSION" ]] \
  && print_step "Updating ${LOCAL_VERSION} → ${REMOTE_VERSION}" \
  || print_step "Installing version ${REMOTE_VERSION}"

print_step "Downloading"

TMPDIR_WORK=$(mktemp -d)
trap 'rm -rf "$TMPDIR_WORK"' EXIT

curl -fsSL --retry 3 --retry-delay 2 "$TARBALL_URL" -o "${TMPDIR_WORK}/skill.tar.gz"
print_ok "Downloaded"

tar -xzf "${TMPDIR_WORK}/skill.tar.gz" -C "$TMPDIR_WORK"
EXTRACTED_DIR=$(find "$TMPDIR_WORK" -maxdepth 1 -mindepth 1 -type d | head -1)
SKILL_SOURCE="${EXTRACTED_DIR}/bitrix"
[[ -d "$SKILL_SOURCE" ]] || { print_error "Unexpected tarball structure."; exit 1; }
print_ok "Extracted"

print_step "Installing to ${INSTALL_DIR}"
mkdir -p "$INSTALL_DIR"
rm -rf "${INSTALL_DIR:?}"/*
cp -r "$SKILL_SOURCE/." "$INSTALL_DIR/"
print_ok "Files copied"

INSTALLED_VERSION=$(tr -d '[:space:]' < "${INSTALL_DIR}/VERSION")
[[ "$INSTALLED_VERSION" == "$REMOTE_VERSION" ]] \
  || { print_error "Version mismatch after install."; exit 1; }

printf "\n\033[1;32mSuccess!\033[0m Bitrix skill %s installed at %s\n" "$REMOTE_VERSION" "$INSTALL_DIR"
printf "Usage: /bitrix <your task>\n\n"
