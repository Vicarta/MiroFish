"""Settings API endpoints."""

from flask import request

from . import settings_bp
from ..services.runtime_settings import get_settings_status, update_runtime_settings


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

    result = update_runtime_settings({
        "LLM_API_KEY": data.get('llm_api_key'),
        "LLM_BASE_URL": data.get('llm_base_url'),
        "LLM_MODEL_NAME": data.get('llm_model_name'),
        "ZEP_API_KEY": data.get('zep_api_key'),
    })

    return {
        "success": True,
        "message": "Settings saved successfully",
        "data": result,
    }
