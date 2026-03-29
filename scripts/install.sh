#!/usr/bin/env bash

set -euo pipefail

if [[ "${OSTYPE:-}" != darwin* && "${OSTYPE:-}" != linux* ]]; then
  echo "Objex installer currently supports macOS and Linux only." >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required but was not found on PATH." >&2
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "git is required but was not found on PATH." >&2
  exit 1
fi

INSTALL_DIR="${OBJEX_INSTALL_DIR:-$HOME/.local/share/objex}"
VENV_DIR="$INSTALL_DIR/.venv"
BIN_DIR="${OBJEX_BIN_DIR:-$HOME/.local/bin}"
REPO_URL="${OBJEX_REPO_URL:-https://github.com/objex/objex.git}"
REPO_REF="${OBJEX_REPO_REF:-main}"
PATH_EXPORT="export PATH=\"$BIN_DIR:\$PATH\""

detect_shell_profile() {
  case "${SHELL:-}" in
    */zsh)
      echo "${HOME}/.zshrc"
      ;;
    */bash)
      if [[ -f "${HOME}/.bash_profile" ]]; then
        echo "${HOME}/.bash_profile"
      else
        echo "${HOME}/.bashrc"
      fi
      ;;
    *)
      echo "${HOME}/.profile"
      ;;
  esac
}

ensure_path_in_profile() {
  local profile_file="$1"

  touch "$profile_file"
  if ! grep -Fqx "$PATH_EXPORT" "$profile_file"; then
    printf '\n%s\n' "$PATH_EXPORT" >> "$profile_file"
  fi
}

mkdir -p "$INSTALL_DIR" "$BIN_DIR"

if [[ -d "$INSTALL_DIR/.git" ]]; then
  git -C "$INSTALL_DIR" fetch --depth 1 origin "$REPO_REF"
  git -C "$INSTALL_DIR" checkout "$REPO_REF"
  git -C "$INSTALL_DIR" reset --hard "origin/$REPO_REF"
else
  rm -rf "$INSTALL_DIR"
  git clone --depth 1 --branch "$REPO_REF" "$REPO_URL" "$INSTALL_DIR"
fi

python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip >/dev/null
"$VENV_DIR/bin/pip" install -e "$INSTALL_DIR" >/dev/null

cat > "$BIN_DIR/objex" <<EOF
#!/usr/bin/env bash
exec "$VENV_DIR/bin/objex" "\$@"
EOF

chmod +x "$BIN_DIR/objex"

PROFILE_FILE="$(detect_shell_profile)"
ensure_path_in_profile "$PROFILE_FILE"

echo "Objex installed successfully."
echo "Binary: $BIN_DIR/objex"
echo "Updated shell profile: $PROFILE_FILE"
echo "Run this now to use 'objex' in the current terminal:"
echo "source \"$PROFILE_FILE\""
