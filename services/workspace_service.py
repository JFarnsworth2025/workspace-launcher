import json
from pathlib import Path
from config import WORKSPACES_DIR
from services.json_service import save_json


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


def save_workspace(workspace: dict, original_name: str | None = None) -> None:
    workspace_file = get_workspace_file(workspace["name"])
    original_file = (
        get_workspace_file(original_name) if original_name is not None else None
    )

    if workspace_file.exists() and original_file != workspace_file:
        raise FileExistsError(f"Workspace '{workspace['name']}' already exists.")

    save_json(workspace_file, workspace)

    if (
        original_file is not None
        and original_file.exists()
        and original_file != workspace_file
    ):
        original_file.unlink(missing_ok=True)


def delete_workspace(workspace_name: str) -> None:
    workspace_file = get_workspace_file(workspace_name)

    if workspace_file.exists():
        workspace_file.unlink()
