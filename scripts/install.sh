#!/usr/bin/env bash

set -euo pipefail

if [[ "${OSTYPE:-}" != darwin* && "${OSTYPE:-}" != linux* ]]; then
  echo "Objex installer currently supports macOS and Linux only." >&2
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "git is required but was not found on PATH." >&2
  exit 1
fi

INSTALL_DIR="${OBJEX_INSTALL_DIR:-$HOME/.local/share/objex}"
VENV_DIR="$INSTALL_DIR/.venv"
REPO_URL="${OBJEX_REPO_URL:-https://github.com/objex/objex.git}"
REPO_REF="${OBJEX_REPO_REF:-main}"

print_logo() {
  cat "$INSTALL_DIR/logo.txt"
}

choose_bin_dir() {
  local candidate
  local path_entry

  if [[ -n "${OBJEX_BIN_DIR:-}" ]]; then
    echo "${OBJEX_BIN_DIR}"
    return
  fi

  IFS=':' read -r -a path_entries <<< "$PATH"
  for path_entry in "${path_entries[@]}"; do
    if [[ -n "$path_entry" && -d "$path_entry" && -w "$path_entry" ]]; then
      echo "$path_entry"
      return
    fi
  done

  for candidate in /opt/homebrew/bin /usr/local/bin "$HOME/.local/bin"; do
    if [[ -d "$candidate" || ! -e "$candidate" ]]; then
      local parent_dir
      parent_dir="$(dirname "$candidate")"
      if [[ -w "$candidate" || ( ! -e "$candidate" && -w "$parent_dir" ) ]]; then
        echo "$candidate"
        return
      fi
    fi
  done

  echo "$HOME/.local/bin"
}

BIN_DIR="$(choose_bin_dir)"
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

pick_python() {
  local candidate

  for candidate in python3.12 python3.11 python3.10 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
      if "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
        echo "$candidate"
        return
      fi
    fi
  done

  echo "Objex requires Python 3.10 or newer, but no supported python3.10+ interpreter was found on PATH." >&2
  exit 1
}

mkdir -p "$INSTALL_DIR" "$BIN_DIR"

PYTHON_BIN="$(pick_python)"

if [[ -d "$INSTALL_DIR/.git" ]]; then
  git -C "$INSTALL_DIR" fetch --depth 1 origin "$REPO_REF"
  git -C "$INSTALL_DIR" checkout "$REPO_REF"
  git -C "$INSTALL_DIR" reset --hard "origin/$REPO_REF"
else
  rm -rf "$INSTALL_DIR"
  git clone --depth 1 --branch "$REPO_REF" "$REPO_URL" "$INSTALL_DIR"
fi

"$PYTHON_BIN" -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip >/dev/null
"$VENV_DIR/bin/pip" install -e "$INSTALL_DIR" >/dev/null

cat > "$BIN_DIR/objex" <<EOF
#!/usr/bin/env bash
exec "$VENV_DIR/bin/objex" "\$@"
EOF

chmod +x "$BIN_DIR/objex"

print_logo
echo "Objex installed successfully."
echo "Binary: $BIN_DIR/objex"

if [[ ":$PATH:" == *":$BIN_DIR:"* ]]; then
  echo "'objex' is available on your PATH."
  echo "Try: objex --help"
else
  PROFILE_FILE="$(detect_shell_profile)"
  ensure_path_in_profile "$PROFILE_FILE"
  echo "Updated shell profile: $PROFILE_FILE"
  echo "Run this now to use 'objex' in the current terminal:"
  echo "source \"$PROFILE_FILE\""
fi
