from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib import error, parse, request


DEFAULT_BASE_URLS = [
    "https://api.objex.app/mcp",
    "https://objexapi-fdxybrx6xq-ue.a.run.app/mcp",
]


class ObjexApiError(RuntimeError):
    """Raised when the Objex API returns an unexpected response."""


@dataclass
class ApiResponse:
    status_code: int
    data: dict[str, Any]


def configured_base_urls() -> list[str]:
    override = os.environ.get("OBJEX_API_BASE_URL", "").strip()
    if override:
        return [override.rstrip("/")]
    return DEFAULT_BASE_URLS


def _request_json(method: str, url: str, payload: dict[str, Any] | None = None) -> ApiResponse:
    body = None
    headers = {"Accept": "application/json"}

    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = request.Request(url=url, method=method, data=body, headers=headers)

    try:
        with request.urlopen(req) as response:
            raw = response.read().decode("utf-8") or "{}"
            data = json.loads(raw)
            return ApiResponse(status_code=response.status, data=data)
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8") or "{}"
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {"message": raw or exc.reason}
        return ApiResponse(status_code=exc.code, data=data)
    except error.URLError as exc:
        raise ObjexApiError(f"Could not reach Objex API: {exc.reason}") from exc


def register_profile(profile: dict[str, Any]) -> ApiResponse:
    last_error: ObjexApiError | None = None
    for base_url in configured_base_urls():
        try:
            return _request_json("POST", base_url, payload=profile)
        except ObjexApiError as exc:
            last_error = exc
    assert last_error is not None
    raise last_error


def get_profile(username: str) -> ApiResponse:
    safe_username = parse.quote(username, safe="")
    last_error: ObjexApiError | None = None
    for base_url in configured_base_urls():
        try:
            return _request_json("GET", f"{base_url}/{safe_username}")
        except ObjexApiError as exc:
            last_error = exc
    assert last_error is not None
    raise last_error


def _gateway_base() -> str:
    override = os.environ.get("OBJEX_API_BASE_URL", "").strip()
    if override:
        return override.rstrip("/").rsplit("/mcp", 1)[0]
    return DEFAULT_BASE_URLS[0].rsplit("/mcp", 1)[0]


def fetch_agents(username: str) -> list[dict[str, Any]]:
    """Fetch registered agents for a user from the Objex Gateway."""
    url = f"{_gateway_base()}/agents/{parse.quote(username, safe='')}"
    try:
        resp = _request_json("GET", url)
        return resp.data.get("agents", [])
    except ObjexApiError:
        return []


def save_agent(username: str, agent: dict[str, Any]) -> ApiResponse:
    """Register or update an agent in the gateway."""
    safe_user = parse.quote(username, safe="")
    safe_agent = parse.quote(agent.get("id", ""), safe="")
    url = f"{_gateway_base()}/agents/{safe_user}/{safe_agent}"
    return _request_json("POST", url, payload=agent)


def save_agent_tools(username: str, agent_id: str, tools: list[dict], environment: str = "dev") -> ApiResponse:
    """Bulk save tools for an agent in the gateway."""
    safe_user = parse.quote(username, safe="")
    safe_agent = parse.quote(agent_id, safe="")
    url = f"{_gateway_base()}/agents/{safe_user}/{safe_agent}/tools"
    return _request_json("POST", url, payload={"tools": tools, "environment": environment})


def upload_codebase_spec(username: str, codebase: str, spec: dict[str, Any]) -> ApiResponse:
    safe_username = parse.quote(username, safe="")
    safe_codebase = parse.quote(codebase, safe="")
    payload = {"codebase": codebase, "openapi": spec}
    last_error: ObjexApiError | None = None
    for base_url in configured_base_urls():
        try:
            return _request_json("POST", f"{base_url}/{safe_username}/{safe_codebase}", payload=payload)
        except ObjexApiError as exc:
            last_error = exc
    assert last_error is not None
    raise last_error
