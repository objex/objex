from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


SUPPORTED_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx"}
TEXT_READ_LIMIT = 512_000
GEMINI_PROMPT_FILE_LIMIT = 120_000
PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
GEMINI_SCAN_PROMPT_PATH = PROMPTS_DIR / "gemini_scan_code.txt"


@dataclass(frozen=True)
class RouteMatch:
    method: str
    path: str
    source_file: str


PYTHON_VERB_DECORATOR = re.compile(
    r"@\w+\.(get|post|put|patch|delete|options|head)\(\s*[\"']([^\"']+)[\"']",
    re.IGNORECASE,
)
PYTHON_ROUTE_DECORATOR = re.compile(
    r"@\w+\.route\(\s*[\"']([^\"']+)[\"'](?P<rest>[^)]*)\)",
    re.IGNORECASE | re.DOTALL,
)
METHODS_LIST = re.compile(r"methods\s*=\s*\[(?P<methods>[^\]]+)\]", re.IGNORECASE)
STRING_LITERAL = re.compile(r"[\"']([A-Za-z]+)[\"']")

JS_ROUTE_HANDLER = re.compile(
    r"\b(?:app|router)\.(get|post|put|patch|delete|options|head)\(\s*[\"'`]([^\"'`]+)[\"'`]",
    re.IGNORECASE,
)
DJANGO_PATH = re.compile(r"\bpath\(\s*[\"']([^\"']+)[\"']", re.IGNORECASE)
DJANGO_RE_PATH = re.compile(r"\bre_path\(\s*r?[\"']([^\"']+)[\"']", re.IGNORECASE)
FASTAPI_ROUTER = re.compile(r"\bAPIRouter\b|\bFastAPI\b", re.IGNORECASE)
BLUEPRINT_HINT = re.compile(r"\bBlueprint\s*\(", re.IGNORECASE)


class GeminiCliNotInstalled(RuntimeError):
    """Raised when Gemini CLI is required but unavailable."""


def require_gemini_cli() -> str:
    gemini_path = shutil.which("gemini")
    if not gemini_path:
        raise GeminiCliNotInstalled(
            "Gemini CLI is not installed. Please install Gemini CLI first, then rerun 'objex scan'."
        )
    return gemini_path


def slugify_codebase(path: Path) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", path.name.strip())
    return cleaned.strip("-") or "codebase"


def normalize_path(raw_path: str) -> str:
    path = raw_path.strip()

    if not path.startswith("/"):
        path = "/" + path

    path = re.sub(r":([A-Za-z_][A-Za-z0-9_]*)", r"{\1}", path)
    path = re.sub(r"<(?:[^:>]+:)?([A-Za-z_][A-Za-z0-9_]*)>", r"{\1}", path)
    path = re.sub(r"/{2,}", "/", path)

    if len(path) > 1 and path.endswith("/"):
        path = path[:-1]

    return path


def iter_source_files(root: Path) -> list[Path]:
    return sorted(
        path for path in root.rglob("*") if path.is_file() and path.suffix in SUPPORTED_EXTENSIONS
    )


def parse_methods(raw: str | None) -> list[str]:
    if not raw:
        return ["GET"]
    return [match.group(1).upper() for match in STRING_LITERAL.finditer(raw)] or ["GET"]


def is_candidate_api_file(file_path: Path, content: str) -> bool:
    lowered = file_path.name.lower()
    if "openapi" in lowered or "swagger" in lowered:
        return False

    patterns = (
        PYTHON_VERB_DECORATOR,
        PYTHON_ROUTE_DECORATOR,
        JS_ROUTE_HANDLER,
        DJANGO_PATH,
        DJANGO_RE_PATH,
        FASTAPI_ROUTER,
        BLUEPRINT_HINT,
    )
    return any(pattern.search(content) for pattern in patterns)


def parse_gemini_output(raw_output: str) -> dict[str, Any]:
    lines = raw_output.splitlines()
    json_start = None
    for index, line in enumerate(lines):
        if line.lstrip().startswith("{"):
            json_start = index
            break

    if json_start is None:
        raise RuntimeError("Gemini CLI did not return JSON output.")

    envelope = json.loads("\n".join(lines[json_start:]))
    response_text = (envelope.get("response") or "").strip()
    if response_text.startswith("```"):
        response_text = re.sub(r"^```(?:json)?\s*", "", response_text)
        response_text = re.sub(r"\s*```$", "", response_text)

    return json.loads(response_text)


def load_gemini_scan_prompt(root: Path, relative_file: str, content: str) -> str:
    template = GEMINI_SCAN_PROMPT_PATH.read_text(encoding="utf-8")
    return template.format(
        repo_root=str(root),
        source_file=relative_file,
        source_code=content[:GEMINI_PROMPT_FILE_LIMIT],
    )


def gemini_extract_operations(
    gemini_path: str,
    root: Path,
    file_path: Path,
    content: str,
) -> list[dict[str, Any]]:
    relative_file = str(file_path.relative_to(root))
    prompt = load_gemini_scan_prompt(root, relative_file, content)

    result = subprocess.run(
        [gemini_path, "-p", prompt, "--output-format", "json"],
        capture_output=True,
        text=True,
        check=False,
        cwd=root,
    )
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        message = stderr or result.stdout.strip() or "unknown Gemini CLI error"
        raise RuntimeError(f"Gemini CLI failed while scanning {relative_file}: {message}")

    parsed = parse_gemini_output(result.stdout)
    apis = parsed.get("apis")
    if not isinstance(apis, list):
        raise RuntimeError(f"Gemini CLI returned invalid API data for {relative_file}.")
    return apis


def scan_codebase(
    root: Path,
    on_file: Callable[[str], None] | None = None,
    on_route: Callable[[RouteMatch], None] | None = None,
) -> tuple[dict, list[RouteMatch]]:
    gemini_path = require_gemini_cli()
    routes: list[RouteMatch] = []
    seen_routes: set[RouteMatch] = set()
    operation_map: dict[RouteMatch, dict[str, Any]] = {}

    def record_route(route: RouteMatch, operation: dict[str, Any]) -> None:
        if route in seen_routes:
            return
        seen_routes.add(route)
        routes.append(route)
        operation_map[route] = operation
        if on_route is not None:
            on_route(route)

    for file_path in iter_source_files(root):
        relative_file = str(file_path.relative_to(root))
        if on_file is not None:
            on_file(relative_file)

        try:
            content = file_path.read_text(encoding="utf-8")[:TEXT_READ_LIMIT]
        except UnicodeDecodeError:
            continue

        if not is_candidate_api_file(file_path, content):
            continue

        for api in gemini_extract_operations(gemini_path, root, file_path, content):
            method = str(api.get("method", "")).upper()
            raw_path = str(api.get("path", "")).strip()
            if not method or not raw_path:
                continue

            route = RouteMatch(
                method=method,
                path=normalize_path(raw_path),
                source_file=relative_file,
            )
            operation = {
                "summary": api.get("summary") or f"{method} {route.path}",
                "operationId": api.get("operationId") or make_operation_id(method, route.path),
                "tags": api.get("tags") or [Path(relative_file).stem],
                "responses": api.get("responses") or {"200": {"description": "Successful response"}},
                "x-objex-source-file": relative_file,
            }
            if api.get("requestBody") is not None:
                operation["requestBody"] = api["requestBody"]

            record_route(route, operation)

    deduped = sorted(routes, key=lambda route: (route.path, route.method, route.source_file))
    spec = build_openapi_spec(root, deduped, operation_map)
    return spec, deduped


def build_openapi_spec(
    root: Path,
    routes: list[RouteMatch],
    operation_map: dict[RouteMatch, dict[str, Any]],
) -> dict:
    codebase = slugify_codebase(root)
    paths: dict[str, dict] = {}

    for route in routes:
        path_item = paths.setdefault(route.path, {})
        path_item[route.method.lower()] = operation_map[route]

    return {
        "openapi": "3.0.3",
        "info": {
            "title": f"{codebase} API Inventory",
            "version": "0.1.0",
            "description": "Generated by Objex CLI from code analysis using Gemini CLI.",
        },
        "paths": paths,
        "servers": [{"url": "https://example.internal", "description": "Replace with actual server URL"}],
    }


def make_operation_id(method: str, path: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", path).strip("_") or "root"
    return f"{method.lower()}_{normalized}"


# ---------------------------------------------------------------------------
# Agent scanning via /capabilities
# ---------------------------------------------------------------------------

def scan_agents(
    username: str = "",
    agent_urls: dict[str, str] | None = None,
    agent_filter: str | None = None,
    on_agent: Callable[[str, str], None] | None = None,
    on_route: Callable[[RouteMatch], None] | None = None,
) -> list[tuple[str, dict, list[RouteMatch]]]:
    """Scan agents by calling their /tools endpoints.

    agent_urls: dict of {agent_id: domain_url} to scan directly.
    If not provided, fetches agent list from the gateway for the given username.

    Returns a list of (agent_id, openapi_spec, routes) tuples.
    """
    import urllib.request as urlreq

    # Build list of agents to scan
    agents_to_scan: dict[str, str] = {}
    if agent_urls:
        agents_to_scan = dict(agent_urls)
    elif username:
        from objex_cli.api import fetch_agents
        for agent in fetch_agents(username):
            aid = agent.get("id", "")
            url = agent.get("domainUrl", "")
            if aid and url:
                agents_to_scan[aid] = url

    results: list[tuple[str, dict, list[RouteMatch]]] = []

    for agent_id, domain_url in agents_to_scan.items():
        if agent_filter and agent_id != agent_filter:
            continue

        if on_agent:
            on_agent(agent_id, domain_url)

        # Call GET /tools on the agent
        tools_list: list[dict] = []
        try:
            req = urlreq.Request(f"{domain_url}/tools", headers={"Accept": "application/json"})
            with urlreq.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            tools_list = data.get("tools", [])
        except Exception:
            results.append((agent_id, {}, []))
            continue

        routes: list[RouteMatch] = []
        operation_map: dict[RouteMatch, dict[str, Any]] = {}

        for tool in tools_list:
            method = str(tool.get("method", "POST")).upper()
            path = normalize_path(str(tool.get("path", "/")))
            route = RouteMatch(method=method, path=path, source_file=f"{agent_id}:/tools")
            routes.append(route)

            operation: dict[str, Any] = {
                "summary": tool.get("description") or f"{method} {path}",
                "operationId": tool.get("id") or make_operation_id(method, f"{agent_id}{path}"),
                "tags": [agent_id],
                "responses": {"200": {"description": "Successful response"}},
            }

            operation_map[route] = operation

            if on_route:
                on_route(route)

        # Build OpenAPI spec
        paths: dict[str, dict] = {}
        for route in routes:
            path_item = paths.setdefault(route.path, {})
            path_item[route.method.lower()] = operation_map[route]

        spec = {
            "openapi": "3.0.3",
            "info": {"title": f"{agent_id} API", "version": "1.0.0"},
            "paths": paths,
            "servers": [{"url": domain_url, "description": agent_id}],
        }

        results.append((agent_id, spec, routes))

    return results
