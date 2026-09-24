import json

from config import SETTINGS_FILE
from services.json_service import save_json

DEFAULT_SETTINGS = {
    "greeting_name": "",
    "launch_on_startup": False,
    "close_to_tray": True,
    "close_applications_on_end": False,
    "check_for_updates": True,
    "motivation_quote": True,
    "bible_verse": True,
}


def load_settings() -> dict:
    settings = DEFAULT_SETTINGS.copy()

    if SETTINGS_FILE.exists():
        with SETTINGS_FILE.open("r", encoding="utf-8") as file:
            saved_settings = json.load(file)

        settings.update(saved_settings)
    return settings


def save_settings(settings: dict) -> None:
    save_json(SETTINGS_FILE, settings)
