"""Configuration management for MiroFish."""

import os
from dotenv import load_dotenv

PROJECT_ROOT_ENV = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../.env')
)
DEFAULT_RUNTIME_ENV = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../runtime-config/settings.env')
)


class Config:
    """Flask config with runtime-reload support."""

    JSON_AS_ASCII = False
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'md', 'txt', 'markdown'}
    DEFAULT_CHUNK_SIZE = 500
    DEFAULT_CHUNK_OVERLAP = 50
    OASIS_SIMULATION_DATA_DIR = os.path.join(os.path.dirname(__file__), '../uploads/simulations')
    OASIS_TWITTER_ACTIONS = [
        'CREATE_POST', 'LIKE_POST', 'REPOST', 'FOLLOW', 'DO_NOTHING', 'QUOTE_POST'
    ]
    OASIS_REDDIT_ACTIONS = [
        'LIKE_POST', 'DISLIKE_POST', 'CREATE_POST', 'CREATE_COMMENT',
        'LIKE_COMMENT', 'DISLIKE_COMMENT', 'SEARCH_POSTS', 'SEARCH_USER',
        'TREND', 'REFRESH', 'DO_NOTHING', 'FOLLOW', 'MUTE'
    ]

    SECRET_KEY = 'mirofish-secret-key'
    DEBUG = True
    LLM_API_KEY = None
    LLM_BASE_URL = 'https://api.openai.com/v1'
    LLM_MODEL_NAME = 'gpt-4o-mini'
    ZEP_API_KEY = None
    OASIS_DEFAULT_MAX_ROUNDS = 10
    REPORT_AGENT_MAX_TOOL_CALLS = 5
    REPORT_AGENT_MAX_REFLECTION_ROUNDS = 2
    REPORT_AGENT_TEMPERATURE = 0.5
    RUNTIME_ENV_FILE = DEFAULT_RUNTIME_ENV

    _runtime_env_mtime = None

    @classmethod
    def runtime_env_file(cls):
        """Return the active runtime env file path."""
        return os.environ.get('MIROFISH_RUNTIME_ENV_FILE', DEFAULT_RUNTIME_ENV)

    @classmethod
    def reload(cls, force=False):
        """Reload config values from the base env and runtime env file."""
        runtime_env_file = cls.runtime_env_file()
        runtime_mtime = (
            os.path.getmtime(runtime_env_file)
            if os.path.exists(runtime_env_file)
            else None
        )

        if not force and runtime_mtime == cls._runtime_env_mtime:
            return

        if os.path.exists(PROJECT_ROOT_ENV):
            load_dotenv(PROJECT_ROOT_ENV, override=False)
        else:
            load_dotenv(override=False)

        if os.path.exists(runtime_env_file):
            load_dotenv(runtime_env_file, override=True)

        cls._runtime_env_mtime = runtime_mtime
        cls.RUNTIME_ENV_FILE = runtime_env_file
        cls.SECRET_KEY = os.environ.get('SECRET_KEY', 'mirofish-secret-key')
        cls.DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
        cls.LLM_API_KEY = os.environ.get('LLM_API_KEY')
        cls.LLM_BASE_URL = os.environ.get('LLM_BASE_URL', 'https://api.openai.com/v1')
        cls.LLM_MODEL_NAME = os.environ.get('LLM_MODEL_NAME', 'gpt-4o-mini')
        cls.ZEP_API_KEY = os.environ.get('ZEP_API_KEY')
        cls.OASIS_DEFAULT_MAX_ROUNDS = int(os.environ.get('OASIS_DEFAULT_MAX_ROUNDS', '10'))
        cls.REPORT_AGENT_MAX_TOOL_CALLS = int(os.environ.get('REPORT_AGENT_MAX_TOOL_CALLS', '5'))
        cls.REPORT_AGENT_MAX_REFLECTION_ROUNDS = int(os.environ.get('REPORT_AGENT_MAX_REFLECTION_ROUNDS', '2'))
        cls.REPORT_AGENT_TEMPERATURE = float(os.environ.get('REPORT_AGENT_TEMPERATURE', '0.5'))

    @classmethod
    def validate(cls):
        """Validate the required runtime config."""
        cls.reload()
        errors = []
        if not cls.LLM_API_KEY:
            errors.append("LLM_API_KEY is not configured")
        if not cls.ZEP_API_KEY:
            errors.append("ZEP_API_KEY is not configured")
        return errors


Config.reload(force=True)
