#!/usr/bin/env bash
# update.sh — Check or update the Bitrix Claude Code skill
# Run:
#   bash ~/.claude/skills/bitrix/update.sh
#   bash ~/.claude/skills/bitrix/update.sh --force
#   bash ~/.claude/skills/bitrix/update.sh --check
set -euo pipefail

REPO="Poliklot/claude-bitrix-skill"
BRANCH="master"
INSTALL_SCRIPT_URL="https://raw.githubusercontent.com/${REPO}/${BRANCH}/install.sh"
REMOTE_VERSION_URL="https://raw.githubusercontent.com/${REPO}/${BRANCH}/bitrix/VERSION"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_VERSION_FILE="${SCRIPT_DIR}/VERSION"

FORCE=false
CHECK_ONLY=false

usage() {
  cat <<'EOF'
Usage:
  bash ~/.claude/skills/bitrix/update.sh
  bash ~/.claude/skills/bitrix/update.sh --force
  bash ~/.claude/skills/bitrix/update.sh --check
EOF
}

read_local_version() {
  if [[ -f "$LOCAL_VERSION_FILE" ]]; then
    tr -d '[:space:]' < "$LOCAL_VERSION_FILE"
  else
    echo ""
  fi
}

read_remote_version() {
  curl -fsSL --retry 3 --retry-delay 2 "$REMOTE_VERSION_URL" | tr -d '[:space:]'
}

normalize_version() {
  local version="${1#v}"
  local major=0
  local minor=0
  local patch=0
  local IFS=.

  read -r major minor patch <<< "$version"
  printf '%05d%05d%05d' "${major:-0}" "${minor:-0}" "${patch:-0}"
}

version_gt() {
  [[ "$(normalize_version "$1")" > "$(normalize_version "$2")" ]]
}

check_mode() {
  local local_version=""
  local remote_version=""

  local_version="$(read_local_version)"
  if ! remote_version="$(read_remote_version)"; then
    echo "CHECK_FAILED reason=remote_version_unavailable"
    return 0
  fi

  if [[ -z "$local_version" ]]; then
    echo "UPDATE_AVAILABLE local=none remote=${remote_version}"
    return 0
  fi

  if version_gt "$remote_version" "$local_version"; then
    echo "UPDATE_AVAILABLE local=${local_version} remote=${remote_version}"
    return 0
  fi

  echo "UP_TO_DATE version=${local_version}"
}

for arg in "$@"; do
  case "$arg" in
    --force)
      FORCE=true
      ;;
    --check)
      CHECK_ONLY=true
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage >&2
      exit 2
      ;;
  esac
done

if [[ "$CHECK_ONLY" == true ]]; then
  check_mode
  exit 0
fi

echo "Checking versions"

REMOTE_VERSION="$(read_remote_version)"
[[ -z "$REMOTE_VERSION" ]] && { echo "Error: Could not fetch remote version" >&2; exit 1; }

LOCAL_VERSION="$(read_local_version)"

if [[ "$FORCE" == false ]]; then
  if [[ -n "$LOCAL_VERSION" && "$LOCAL_VERSION" == "$REMOTE_VERSION" ]]; then
    echo "Already up to date (${LOCAL_VERSION})"
    exit 0
  fi

  if [[ -n "$LOCAL_VERSION" ]] && version_gt "$LOCAL_VERSION" "$REMOTE_VERSION"; then
    echo "Installed version (${LOCAL_VERSION}) is newer than remote (${REMOTE_VERSION})"
    exit 0
  fi
fi

echo "Fetching latest installer from GitHub..."
SCRIPT="$(curl -fsSL --retry 3 --retry-delay 2 "$INSTALL_SCRIPT_URL")"
[[ -z "$SCRIPT" ]] && { echo "Error: Could not download install.sh" >&2; exit 1; }

if [[ "$FORCE" == true ]]; then
  exec bash -c "$SCRIPT" -- --force
fi

exec bash -c "$SCRIPT"
