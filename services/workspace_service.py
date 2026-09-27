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


def validate_loaded_workspace(data: object, source: Path) -> dict:
    if not isinstance(data, dict):
        raise ValueError("Workspace must be a JSON object.")
    expected = get_workspace_file(data.get("name"))
    if expected.name.lower() != source.name.lower():
        raise ValueError("Filename does not match the workspace name.")
    if source.resolve().parent != WORKSPACES_DIR.resolve():
        raise ValueError("Workspace file points outside the workspace directory.")
    order = data.get("order", 1)
    if type(order) is not int:
        raise ValueError("Display order must be an integer.")
    if order < 1 or order > 999:
        raise ValueError("Display order must be an integer between 1 and 999.")
    applications = data.get("applications", [])
    if not isinstance(applications, list):
        raise ValueError("Workspace items must be a list.")
    for item in applications:
        if not isinstance(item, dict):
            raise ValueError("Each workspace item must be a JSON object.")

        name = item.get("name")
        path = item.get("path")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Each item needs a name.")
        if not isinstance(path, str) or not path.strip():
            raise ValueError("Each item needs a path or URL.")
        if "\x00" in name or "\x00" in path:
            raise ValueError("Item names and paths cannot contain null characters.")

        launch_type = item.get("launch_type", "application")
        if launch_type != "application" and launch_type != "resource":
            raise ValueError("Item launch type must be application or resource.")

        arguments = item.get("arguments", [])
        if not isinstance(arguments, list):
            raise ValueError("Item arguments must be a list.")
        for argument in arguments:
            if not isinstance(argument, str) or "\x00" in argument:
                raise ValueError("Each argument must be text without null characters.")

    workspace = data.copy()
    workspace["order"] = order
    workspace["applications"] = applications
    return workspace


def load_workspaces(errors: list[str] | None = None) -> list[dict]:
    """Collect file errors when a list is supplied; otherwise raise them."""
    workspaces = []

    try:
        files = sorted(WORKSPACES_DIR.iterdir())
    except OSError as error:
        if errors is None:
            raise
        errors.append(f"Could not read workspace directory: {error}")
        return []

    for workspace_file in files:
        if workspace_file.suffix.lower() != ".json":
            continue
        try:
            with workspace_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
            workspace = validate_loaded_workspace(data, workspace_file)
            workspaces.append(workspace)
        except (OSError, ValueError, RuntimeError, RecursionError) as error:
            if errors is None:
                raise
            errors.append(f"{workspace_file.name}: {error}")

    workspaces.sort(key=lambda workspace: workspace["order"])

    return workspaces


def save_workspace(workspace: dict, original_name: str | None = None) -> None:
    workspace_file = get_workspace_file(workspace["name"])
    original_file = None
    if original_name is not None:
        original_file = get_workspace_file(original_name)

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
