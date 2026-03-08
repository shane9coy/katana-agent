from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

HOME = Path.home()
HERMES_DIR = Path(os.environ.get("HERMES_HOME", HOME / ".hermes")).expanduser()
ORACLE_STATE_DIR = Path(os.environ.get("ORACLE_STATE_DIR", HERMES_DIR / "oracle")).expanduser()
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
CACHE_DIR = ORACLE_STATE_DIR / "cache"
REPORTS_DIR = ORACLE_STATE_DIR / "reports"
JOURNAL_DIR = ORACLE_STATE_DIR / "journal"
USER_PROFILE_PATH = ORACLE_STATE_DIR / "user_profile.json"
CONSENT_PATH = ORACLE_STATE_DIR / "consent.yaml"
SCORING_WEIGHTS_PATH = ORACLE_STATE_DIR / "scoring_weights.yaml"
ENV_PATH = ORACLE_STATE_DIR / ".env"
ENV_EXAMPLE_PATH = ORACLE_STATE_DIR / ".env.example"
GOOGLE_API_PATH = HERMES_DIR / "skills" / "productivity" / "google-workspace" / "scripts" / "google_api.py"
DEFAULT_TIMEOUT = 60


class OracleHTTPError(RuntimeError):
    def __init__(self, status: int, body: str, url: str):
        self.status = status
        self.body = body
        self.url = url
        super().__init__(f"HTTP {status} for {url}: {body[:200]}")


def ensure_runtime_dirs() -> None:
    ORACLE_STATE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    JOURNAL_DIR.mkdir(parents=True, exist_ok=True)


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_env_file(path: Path | None = None) -> dict[str, str]:
    target = path or ENV_PATH
    values: dict[str, str] = {}
    if not target.exists():
        return values
    for raw_line in target.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def get_env(key: str, default: str | None = None) -> str | None:
    env_file_values = load_env_file()
    return os.environ.get(key) or env_file_values.get(key) or default


def load_json_file(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return {} if default is None else default
    return json.loads(text)


def save_json_file(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def _parse_scalar(value: str) -> Any:
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value in {"null", "Null", "none", "None", "~"}:
        return None
    if re.fullmatch(r"-?\d+", value):
        try:
            return int(value)
        except ValueError:
            pass
    if re.fullmatch(r"-?\d+\.\d+", value):
        try:
            return float(value)
        except ValueError:
            pass
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def load_simple_yaml(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    lines = path.read_text(encoding="utf-8").splitlines()
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]

    for raw_line in lines:
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        stripped = raw_line.strip()
        if ":" not in stripped:
            continue

        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()

        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()

        parent = stack[-1][1]
        if value == "":
            node: dict[str, Any] = {}
            parent[key] = node
            stack.append((indent, node))
        else:
            parent[key] = _parse_scalar(value)

    return root if root else ({} if default is None else default)


def dump_simple_yaml(data: Any, indent: int = 0) -> str:
    spaces = " " * indent
    if isinstance(data, dict):
        lines: list[str] = []
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{spaces}{key}:")
                lines.append(dump_simple_yaml(value, indent + 2))
            else:
                lines.append(f"{spaces}{key}: {format_yaml_scalar(value)}")
        return "\n".join(lines)
    if isinstance(data, list):
        return "\n".join(f"{spaces}- {format_yaml_scalar(item)}" for item in data)
    return f"{spaces}{format_yaml_scalar(data)}"


def format_yaml_scalar(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if not text or any(ch in text for ch in [":", "#", "\n"]):
        return json.dumps(text)
    return text


def save_simple_yaml(path: Path, data: Any, header: str | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = dump_simple_yaml(data).rstrip() + "\n"
    if header:
        body = header.rstrip() + "\n\n" + body
    path.write_text(body, encoding="utf-8")


def stable_hash(*parts: Any) -> str:
    normalized = json.dumps(parts, sort_keys=True, default=str)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def cache_file_path(kind: str, key_parts: Iterable[Any]) -> Path:
    digest = stable_hash(kind, list(key_parts))
    return CACHE_DIR / f"{kind}-{digest}.json"


def load_cache(kind: str, key_parts: Iterable[Any], ttl_seconds: int | None) -> dict[str, Any] | None:
    path = cache_file_path(kind, key_parts)
    if not path.exists():
        return None
    data = load_json_file(path, default={})
    if ttl_seconds is None:
        return data
    created_at = data.get("cache_meta", {}).get("created_at")
    if not created_at:
        return None
    try:
        created_dt = datetime.fromisoformat(created_at)
    except ValueError:
        return None
    age_seconds = (datetime.now(timezone.utc) - created_dt.astimezone(timezone.utc)).total_seconds()
    if age_seconds > ttl_seconds:
        return None
    return data


def save_cache(kind: str, key_parts: Iterable[Any], payload: dict[str, Any]) -> Path:
    path = cache_file_path(kind, key_parts)
    payload = dict(payload)
    payload.setdefault("cache_meta", {})
    payload["cache_meta"].setdefault("created_at", iso_now())
    save_json_file(path, payload)
    return path


def http_json_request(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    payload: Any = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> Any:
    raw_data = None
    request_headers = headers.copy() if headers else {}

    if payload is not None:
        raw_data = json.dumps(payload).encode("utf-8") if not isinstance(payload, (bytes, bytearray)) else payload
        request_headers.setdefault("Content-Type", "application/json")

    request_obj = urllib_request.Request(url, data=raw_data, headers=request_headers, method=method.upper())
    try:
        with urllib_request.urlopen(request_obj, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except urllib_error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise OracleHTTPError(exc.code, body, url) from exc
    except urllib_error.URLError as exc:
        raise RuntimeError(f"Network error calling {url}: {exc}") from exc

    stripped = body.strip()
    if not stripped:
        return {}
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return {"raw": stripped}


def query_url(base_url: str, query: dict[str, Any] | None = None) -> str:
    if not query:
        return base_url
    encoded = urllib_parse.urlencode({k: v for k, v in query.items() if v is not None})
    return f"{base_url}?{encoded}"


def recursive_find_values(data: Any, key_names: set[str]) -> list[Any]:
    found: list[Any] = []
    if isinstance(data, dict):
        for key, value in data.items():
            if key.lower() in key_names:
                found.append(value)
            found.extend(recursive_find_values(value, key_names))
    elif isinstance(data, list):
        for item in data:
            found.extend(recursive_find_values(item, key_names))
    return found


def recursive_find_first(data: Any, key_names: set[str], default: Any = None) -> Any:
    values = recursive_find_values(data, key_names)
    return values[0] if values else default


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]
