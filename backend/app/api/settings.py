"""Settings API endpoints."""

from flask import request

from . import settings_bp
from ..services.runtime_settings import get_settings_status, update_runtime_settings
from ..services.settings_validation import SettingsValidationError


@settings_bp.route('', methods=['GET'])
def get_settings():
    """Return write-safe runtime settings state."""
    return {
        "success": True,
        "data": get_settings_status(),
    }


@settings_bp.route('', methods=['PUT'])
def save_settings():
    """Persist operator-provided runtime settings."""
    data = request.get_json(silent=True) or {}

    try:
        result = update_runtime_settings({
            "LLM_API_KEY": data.get('llm_api_key'),
            "LLM_BASE_URL": data.get('llm_base_url'),
            "LLM_MODEL_NAME": data.get('llm_model_name'),
            "ZEP_API_KEY": data.get('zep_api_key'),
        })
    except SettingsValidationError as exc:
        return {
            "success": False,
            "error": str(exc),
            "field": exc.field,
        }, 400

    return {
        "success": True,
        "message": "Settings validated and saved successfully",
        "data": result,
    }
