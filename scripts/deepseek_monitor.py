from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from scripts.notifications import send_whatsapp_notification

STATE_PATH = Path(".github/deepseek-monitor-state.json")
DEFAULT_TARGETS = {
    "deepseek-pricing": "https://api-docs.deepseek.com/quick_start/pricing",
    "deepseek-updates": "https://api-docs.deepseek.com/updates",
}


@dataclass(frozen=True)
class MonitorTarget:
    name: str
    url: str


@dataclass(frozen=True)
class FetchResult:
    status_code: int
    content_hash: str
    content_length: int


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_targets(raw_targets: str | None = None) -> list[MonitorTarget]:
    if not raw_targets:
        return [
            MonitorTarget(name=name, url=url) for name, url in DEFAULT_TARGETS.items()
        ]

    targets = []
    for raw_target in raw_targets.split(","):
        raw_target = raw_target.strip()
        if not raw_target:
            continue

        if "=" not in raw_target:
            raise ValueError(
                "DEEPSEEK_MONITOR_TARGETS entries must use name=url format."
            )

        name, url = raw_target.split("=", 1)
        name = name.strip()
        url = url.strip()
        if not name or not url:
            raise ValueError("DEEPSEEK_MONITOR_TARGETS contains an empty name or URL.")
        targets.append(MonitorTarget(name=name, url=url))

    return targets


def hash_content(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def fetch_target(target: MonitorTarget) -> FetchResult:
    try:
        import requests
    except ImportError as error:
        raise RuntimeError("requests is not installed") from error

    response = requests.get(
        target.url,
        headers={
            "User-Agent": "luismarrero.me-deepseek-monitor/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml,text/plain,*/*",
        },
        timeout=30,
    )
    response.raise_for_status()
    return FetchResult(
        status_code=response.status_code,
        content_hash=hash_content(response.content),
        content_length=len(response.content),
    )


def load_state(path: Path = STATE_PATH) -> dict[str, object]:
    if not path.exists():
        return {}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    return data if isinstance(data, dict) else {}


def save_state(state: dict[str, object], path: Path = STATE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def monitor_targets(
    targets: list[MonitorTarget],
    state: dict[str, object],
    *,
    checked_at: str | None = None,
) -> tuple[dict[str, object], list[str], list[str]]:
    checked_at = checked_at or utc_now_iso()
    stored_targets = state.get("targets")
    if not isinstance(stored_targets, dict):
        stored_targets = {}

    new_targets: dict[str, object] = dict(stored_targets)
    changes = []
    errors = []

    for target in targets:
        try:
            result = fetch_target(target)
        except Exception as error:
            errors.append(f"{target.name}: {error.__class__.__name__}")
            continue

        previous = stored_targets.get(target.name)
        previous_hash = (
            previous.get("content_hash") if isinstance(previous, dict) else None
        )
        is_first_seen = previous_hash is None
        has_changed = previous_hash is not None and previous_hash != result.content_hash
        last_changed_at = (
            checked_at
            if is_first_seen or has_changed
            else previous.get("last_changed_at")
            if isinstance(previous, dict)
            else checked_at
        )

        new_targets[target.name] = {
            "url": target.url,
            "content_hash": result.content_hash,
            "content_length": result.content_length,
            "status_code": result.status_code,
            "last_checked_at": checked_at,
            "last_changed_at": last_changed_at,
        }

        if has_changed or (
            is_first_seen
            and os.getenv("DEEPSEEK_MONITOR_ALERT_ON_FIRST_RUN", "").lower()
            in {"1", "true", "yes"}
        ):
            changes.append(f"{target.name}: {target.url}")

    new_state = {
        "last_checked_at": checked_at,
        "targets": new_targets,
    }
    return new_state, changes, errors


def build_monitor_message(changes: list[str], errors: list[str]) -> str:
    lines = ["DeepSeek monitor"]
    if changes:
        lines.append("Cambios detectados:")
        lines.extend(f"- {change}" for change in changes)
    if errors:
        lines.append("Errores de monitoreo:")
        lines.extend(f"- {error}" for error in errors)
    return "\n".join(lines)


def main() -> None:
    targets = parse_targets(os.getenv("DEEPSEEK_MONITOR_TARGETS"))
    state = load_state()
    new_state, changes, errors = monitor_targets(targets, state)
    save_state(new_state)

    if changes or errors:
        message = build_monitor_message(changes, errors)
        print(message)
        send_whatsapp_notification(message)
    else:
        print("DeepSeek monitor: no changes detected.")


if __name__ == "__main__":
    main()
