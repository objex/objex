from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from objex_cli.api import ObjexApiError, get_profile, register_profile, upload_codebase_spec
from objex_cli.scanner import scan_codebase, slugify_codebase
from objex_cli.storage import list_profiles, load_profile, save_profile, save_spec


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ASCII_LOGO = r"""
   \ 
    \ 
     \ 
      \ 
   >---\ 
    \   \
     \   \
      \   \
       \___\    o

objex
""".strip("\n")


def main() -> None:
    print(ASCII_LOGO)
    parser = build_parser()
    args = parser.parse_args()

    if not hasattr(args, "handler"):
        parser.print_help()
        return

    try:
        args.handler(args)
    except ObjexApiError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        raise SystemExit(130) from None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="objex", description="Objex CLI service")
    subparsers = parser.add_subparsers(dest="command")

    install_parser = subparsers.add_parser("install", help="Register this installation with Objex")
    install_parser.add_argument("--username")
    install_parser.add_argument("--company-name")
    install_parser.add_argument("--contact-person")
    install_parser.add_argument("--email")
    install_parser.set_defaults(handler=handle_install)

    scan_parser = subparsers.add_parser("scan", help="Scan a codebase and upload an OpenAPI spec")
    scan_parser.add_argument("--username")
    scan_parser.add_argument("--codebase", help="Path to the codebase to scan")
    scan_parser.add_argument("--codebase-name", help="Optional identifier used for storage and upload")
    scan_parser.set_defaults(handler=handle_scan)

    update_parser = subparsers.add_parser("update", help="Refresh a local profile from Objex API")
    update_parser.add_argument("--username")
    update_parser.set_defaults(handler=handle_update)

    list_parser = subparsers.add_parser("list", help="List locally installed Objex profiles")
    list_parser.set_defaults(handler=handle_list)

    whoami_parser = subparsers.add_parser("whoami", help="Show the locally installed Objex profile")
    whoami_parser.add_argument("--username")
    whoami_parser.set_defaults(handler=handle_whoami)

    return parser


def prompt(label: str, validator=None) -> str:
    while True:
        value = input(f"{label}: ").strip()
        if not value:
            print("A value is required.", file=sys.stderr)
            continue
        if validator and not validator(value):
            continue
        return value


def validate_username(username: str) -> bool:
    if " " in username:
        print("Username cannot contain spaces.", file=sys.stderr)
        return False
    return True


def validate_email(email: str) -> bool:
    if not EMAIL_PATTERN.match(email):
        print("Please enter a valid email address.", file=sys.stderr)
        return False
    return True


def handle_install(args: argparse.Namespace) -> None:
    username = args.username or prompt("Username", validate_username)
    company_name = args.company_name or prompt("Company name")
    contact_person = args.contact_person or prompt("Contact person")
    email = args.email or prompt("Email address", validate_email)

    profile = {
        "username": username,
        "companyName": company_name,
        "contactPerson": contact_person,
        "email": email,
    }

    response = register_profile(profile)
    if 200 <= response.status_code < 300:
        profile.update(response.data)
        path = save_profile(username, profile)
        print(f"Installation successful. Profile saved to {path}")
        return

    existing = get_profile(username)
    if 200 <= existing.status_code < 300:
        existing_contact = existing.data.get("contactPerson", "unknown contact")
        existing_email = existing.data.get("email", "unknown email")
        print(
            f"This app is already registered. Please contact {existing_contact} at {existing_email}.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    message = response.data.get("message", "Registration failed.")
    raise ObjexApiError(message)


def handle_scan(args: argparse.Namespace) -> None:
    username = args.username or prompt("Username", validate_username)
    profile = load_profile(username)
    if not profile:
        print(
            f"No local installation found for '{username}'. Run 'objex install' first.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    codebase_input = args.codebase or prompt("Codebase path")
    codebase_path = Path(codebase_input).expanduser().resolve()
    if not codebase_path.exists() or not codebase_path.is_dir():
        print(f"Codebase path does not exist or is not a directory: {codebase_path}", file=sys.stderr)
        raise SystemExit(1)

    codebase_name = args.codebase_name or slugify_codebase(codebase_path)
    spec, routes = scan_codebase(codebase_path)
    spec_path = save_spec(username, codebase_name, spec)

    response = upload_codebase_spec(username, codebase_name, spec)
    if not (200 <= response.status_code < 300):
        message = response.data.get("message", "Upload failed.")
        raise ObjexApiError(message)

    print(f"Scan successful for '{codebase_name}'.")
    print(f"Detected {len(routes)} routes.")
    print(f"Spec saved to {spec_path}")


def handle_update(args: argparse.Namespace) -> None:
    username = args.username or prompt("Username", validate_username)
    profile = load_profile(username)
    if not profile:
        print(f"No local installation found for '{username}'.", file=sys.stderr)
        raise SystemExit(1)

    response = get_profile(username)
    if not (200 <= response.status_code < 300):
        message = response.data.get("message", "Could not refresh profile.")
        raise ObjexApiError(message)

    merged = {**profile, **response.data}
    path = save_profile(username, merged)
    print(f"Profile updated from Objex API and saved to {path}")


def handle_list(_: argparse.Namespace) -> None:
    usernames = list_profiles()
    if not usernames:
        print("No local Objex installations found.")
        return

    print(json.dumps(usernames, indent=2))


def handle_whoami(args: argparse.Namespace) -> None:
    usernames = list_profiles()
    if not usernames:
        print("No local Objex installations found.", file=sys.stderr)
        raise SystemExit(1)

    username = args.username
    if not username:
        if len(usernames) == 1:
            username = usernames[0]
        else:
            print(
                "Multiple local Objex installations found. Use 'objex whoami --username <username>'.",
                file=sys.stderr,
            )
            raise SystemExit(1)

    profile = load_profile(username)
    if not profile:
        print(f"No local installation found for '{username}'.", file=sys.stderr)
        raise SystemExit(1)

    print(json.dumps(profile, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
