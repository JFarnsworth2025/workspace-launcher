import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

APP_NAME = "Workspace Launcher"
APP_AUTHOR = "Pariven"
APP_VERSION = "0.1.0"

APP_DATA_DIR = Path(os.environ["LOCALAPPDATA"]) / APP_AUTHOR / APP_NAME

WORKSPACES_DIR = APP_DATA_DIR / "workspaces"
LOGS_DIR = APP_DATA_DIR / "logs"

SETTINGS_FILE = APP_DATA_DIR / "settings.json"
HISTORY_FILE = APP_DATA_DIR / "workspace_history.json"
QUOTE_CACHE_FILE = APP_DATA_DIR / "quote_cache.json"
LOG_FILE = LOGS_DIR / "workspace_launcher.log"

VERSES_FILE = PROJECT_ROOT / "data" / "daily_verses.json"

APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
WORKSPACES_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
