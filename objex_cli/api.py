from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib import error, parse, request


BASE_URL = "https://api.objex.app/mcp"


class ObjexApiError(RuntimeError):
    """Raised when the Objex API returns an unexpected response."""


@dataclass
class ApiResponse:
    status_code: int
    data: dict[str, Any]


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
    return _request_json("POST", BASE_URL, payload=profile)


def get_profile(username: str) -> ApiResponse:
    safe_username = parse.quote(username, safe="")
    return _request_json("GET", f"{BASE_URL}/{safe_username}")


def upload_codebase_spec(username: str, codebase: str, spec: dict[str, Any]) -> ApiResponse:
    safe_username = parse.quote(username, safe="")
    safe_codebase = parse.quote(codebase, safe="")
    payload = {"codebase": codebase, "openapi": spec}
    return _request_json("POST", f"{BASE_URL}/{safe_username}/{safe_codebase}", payload=payload)
