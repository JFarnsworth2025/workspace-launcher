import json

from config import HISTORY_FILE


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

    with HISTORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(history, file, indent=4)
