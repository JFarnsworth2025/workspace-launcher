import json
import ntpath
from pathlib import Path
from config import WORKSPACES_DIR
from services.json_service import save_json


def get_workspace_file(workspace_name: str) -> Path:
    if not isinstance(workspace_name, str) or not workspace_name.strip():
        raise ValueError("Workspace name cannot be empty.")
    if workspace_name != workspace_name.strip():
        raise ValueError("Workspace name cannot start or end with whitespace.")
    if len(workspace_name) > 120:
        raise ValueError("Workspace name must be 120 characters or fewer.")
    if workspace_name.endswith(".") or ntpath.isreserved(workspace_name):
        raise ValueError(
            'Use a Windows-safe workspace name: no reserved names, trailing dots, '
            'or characters such as < > : " / \\ | ? *.'
        )
    filename = workspace_name.lower().replace(" ", "_")
    path = WORKSPACES_DIR / f"{filename}.json"
    if ntpath.isreserved(path.name):
        raise ValueError("That workspace name is reserved by Windows.")
    if path.resolve().parent != WORKSPACES_DIR.resolve():
        raise ValueError("Workspace files must stay inside the workspace directory.")
    return path


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
