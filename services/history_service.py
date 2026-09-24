import json

from config import HISTORY_FILE
from services.json_service import save_json


def load_history() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []

    with HISTORY_FILE.open("r", encoding="utf-8") as file:
        history = json.load(file)

    if not isinstance(history, list):
        raise ValueError("Workspace history must contain a list.")

    return history


def save_session(session_record: dict) -> None:
    history = load_history()
    history.append(session_record)

    save_json(HISTORY_FILE, history)
