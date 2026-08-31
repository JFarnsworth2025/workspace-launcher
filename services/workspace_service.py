import json
from pathlib import Path
from config import WORKSPACES_DIR


def get_workspace_file(workspace_name: str) -> Path:
    filename = workspace_name.lower().replace(" ", "_")
    return WORKSPACES_DIR / f"{filename}.json"


def load_workspaces() -> list[dict]:
    workspaces = []

    for workspace_file in WORKSPACES_DIR.glob("*.json"):
        with workspace_file.open("r", encoding="utf-8") as file:
            workspace = json.load(file)

        workspaces.append(workspace)

    workspaces.sort(key=lambda workspace: workspace.get("order", 0))

    return workspaces


def save_workspace(workspace: dict) -> None:
    workspace_file = get_workspace_file(workspace["name"])

    with workspace_file.open("w", encoding="utf-8") as file:
        json.dump(workspace, file, indent=4)


def delete_workspace(workspace_name: str) -> None:
    workspace_file = get_workspace_file(workspace_name)

    if workspace_file.exists():
        workspace_file.unlink()
