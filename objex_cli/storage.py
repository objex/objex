from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CONFIG_ROOT = Path.home() / ".objex"


def ensure_root() -> Path:
    CONFIG_ROOT.mkdir(parents=True, exist_ok=True)
    return CONFIG_ROOT


def user_dir(username: str) -> Path:
    return ensure_root() / username


def profile_path(username: str) -> Path:
    return user_dir(username) / "profile.json"


def spec_path(username: str, codebase: str) -> Path:
    return user_dir(username) / f"{codebase}-openapi.json"


def save_profile(username: str, profile: dict[str, Any]) -> Path:
    directory = user_dir(username)
    directory.mkdir(parents=True, exist_ok=True)
    path = profile_path(username)
    path.write_text(json.dumps(profile, indent=2, sort_keys=True), encoding="utf-8")
    return path


def load_profile(username: str) -> dict[str, Any] | None:
    path = profile_path(username)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_spec(username: str, codebase: str, spec: dict[str, Any]) -> Path:
    directory = user_dir(username)
    directory.mkdir(parents=True, exist_ok=True)
    path = spec_path(username, codebase)
    path.write_text(json.dumps(spec, indent=2, sort_keys=True), encoding="utf-8")
    return path


def list_profiles() -> list[str]:
    if not CONFIG_ROOT.exists():
        return []
    return sorted(
        path.name
        for path in CONFIG_ROOT.iterdir()
        if path.is_dir() and (path / "profile.json").exists()
    )
