"""Runtime settings persistence for operator-managed configuration."""

import os
from typing import Dict, Any

from dotenv import dotenv_values

from ..config import Config

EDITABLE_FIELDS = (
    'LLM_API_KEY',
    'LLM_BASE_URL',
    'LLM_MODEL_NAME',
    'ZEP_API_KEY',
)

SECRET_FIELDS = {'LLM_API_KEY', 'ZEP_API_KEY'}


def _normalize_value(value: Any) -> str:
    if value is None:
        return ''
    return str(value).strip()


def _quote_env_value(value: str) -> str:
    escaped = value.replace('\\', '\\\\').replace('"', '\\"')
    return f'"{escaped}"'


def _runtime_env_path() -> str:
    return Config.runtime_env_file()


def get_settings_status() -> Dict[str, Any]:
    """Return non-secret runtime settings status for UI consumption."""
    Config.reload()
    return {
        "llm_api_key_configured": bool(Config.LLM_API_KEY),
        "zep_api_key_configured": bool(Config.ZEP_API_KEY),
        "llm_base_url": Config.LLM_BASE_URL,
        "llm_model_name": Config.LLM_MODEL_NAME,
    }


def update_runtime_settings(updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Persist runtime settings and refresh active config.

    Secret fields are write-only from the API perspective.
    Blank inputs mean "leave unchanged".
    """
    filtered_updates: Dict[str, str] = {}

    for field in EDITABLE_FIELDS:
        if field not in updates:
            continue
        value = _normalize_value(updates[field])
        if not value:
            continue
        filtered_updates[field] = value

    if not filtered_updates:
        return {
            "updated_fields": [],
            "status": get_settings_status(),
        }

    env_path = _runtime_env_path()
    os.makedirs(os.path.dirname(env_path), exist_ok=True)

    existing = {}
    if os.path.exists(env_path):
        existing = {
            key: value
            for key, value in dotenv_values(env_path).items()
            if value is not None
        }

    existing.update(filtered_updates)

    lines = [
        "# Operator-managed runtime settings for MiroFish",
        "# Secret values are write-only in the UI and must not be returned by the API.",
    ]
    for key in EDITABLE_FIELDS:
        if key in existing:
            lines.append(f"{key}={_quote_env_value(existing[key])}")

    with open(env_path, 'w', encoding='utf-8') as handle:
        handle.write("\n".join(lines) + "\n")
    os.chmod(env_path, 0o600)

    for key, value in filtered_updates.items():
        os.environ[key] = value

    Config.reload(force=True)

    return {
        "updated_fields": [
            field.lower()
            for field in filtered_updates.keys()
        ],
        "status": get_settings_status(),
    }
