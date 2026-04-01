"""Validation helpers for operator-managed runtime settings."""

from __future__ import annotations

import urllib.error
import urllib.request
from typing import Any, Dict, Iterable

from openai import OpenAI


class SettingsValidationError(ValueError):
    """Raised when runtime settings fail validation."""

    def __init__(self, message: str, field: str | None = None):
        super().__init__(message)
        self.field = field


def _normalize_base_url(base_url: str) -> str:
    normalized = (base_url or '').strip().rstrip('/')
    if normalized.endswith('/chat/completions'):
        raise SettingsValidationError(
            'LLM base URL must point to the provider root (for example, https://openrouter.ai/api/v1), not to /chat/completions.',
            field='llm_base_url',
        )
    return normalized


def _extract_error_message(exc: Exception) -> str:
    response = getattr(exc, 'response', None)
    if response is not None:
        try:
            payload = response.json()
            if isinstance(payload, dict):
                if isinstance(payload.get('error'), dict):
                    message = payload['error'].get('message')
                    if message:
                        return str(message)
                if payload.get('error'):
                    return str(payload['error'])
                if payload.get('message'):
                    return str(payload['message'])
        except Exception:
            pass

        text = getattr(response, 'text', '')
        if text:
            return text[:400].strip()

        status_code = getattr(response, 'status_code', None)
        if status_code:
            return f'HTTP {status_code}'

    body = getattr(exc, 'body', None)
    if body:
        return str(body)[:400]

    return str(exc)[:400]


def validate_llm_settings(api_key: str, base_url: str, model_name: str) -> None:
    """Validate an OpenAI-compatible provider by performing a tiny completion call."""
    if not api_key:
        raise SettingsValidationError('LLM API key is required for validation.', field='llm_api_key')
    if not base_url:
        raise SettingsValidationError('LLM base URL is required for validation.', field='llm_base_url')
    if not model_name:
        raise SettingsValidationError('LLM model name is required for validation.', field='llm_model_name')

    normalized_base_url = _normalize_base_url(base_url)

    try:
        client = OpenAI(
            api_key=api_key,
            base_url=normalized_base_url,
            timeout=20.0,
        )
        client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Reply with OK."}],
            max_tokens=1,
            temperature=0,
        )
    except SettingsValidationError:
        raise
    except Exception as exc:
        raise SettingsValidationError(
            f'LLM settings validation failed: {_extract_error_message(exc)}',
            field='llm_api_key',
        ) from exc


def validate_zep_api_key(api_key: str) -> None:
    """Validate the Zep credential against the graph list endpoint."""
    if not api_key:
        raise SettingsValidationError('Zep API key is required for validation.', field='zep_api_key')

    request = urllib.request.Request(
        'https://api.getzep.com/api/v2/graph',
        headers={
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json',
            'User-Agent': 'MiroFish Settings Validation',
        },
        method='GET',
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            response.read(1)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode('utf-8', errors='ignore')
        message = body.strip()
        if not message:
            message = f'HTTP {exc.code}'
        raise SettingsValidationError(
            f'Zep API key validation failed: {message[:400]}',
            field='zep_api_key',
        ) from exc
    except Exception as exc:
        raise SettingsValidationError(
            f'Zep API key validation failed: {str(exc)[:400]}',
            field='zep_api_key',
        ) from exc


def validate_runtime_settings(candidate: Dict[str, str], changed_fields: Iterable[str]) -> None:
    """Validate changed runtime settings before persisting them."""
    changed = set(changed_fields)

    if changed.intersection({'LLM_API_KEY', 'LLM_BASE_URL', 'LLM_MODEL_NAME'}):
        validate_llm_settings(
            api_key=candidate.get('LLM_API_KEY', ''),
            base_url=candidate.get('LLM_BASE_URL', ''),
            model_name=candidate.get('LLM_MODEL_NAME', ''),
        )

    if 'ZEP_API_KEY' in changed:
        validate_zep_api_key(candidate.get('ZEP_API_KEY', ''))
