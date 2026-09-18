import os
import subprocess

from services.workspace_session_service import WorkspaceSession

running_processes: list[tuple[str, subprocess.Popen]] = []
active_workspace_name: str | None = None

active_session = WorkspaceSession()


def get_active_workspace_name() -> str | None:
    return active_workspace_name


def get_running_applications() -> list[str]:
    running_processes[:] = [
        (name, process) for name, process in running_processes if process.poll() is None
    ]
    return [name for name, _ in running_processes]


def launch_workspace(workspace: dict) -> tuple[int, list[str]]:

    global active_workspace_name

    if active_workspace_name is not None:
        raise ValueError(
            f"Cannot launch workspace '{workspace['name']}' because workspace '{active_workspace_name}' is already running."
        )

    successful_launches = 0
    launch_errors = []

    get_running_applications()

    for application in workspace["applications"]:
        try:
            if application.get("launch_type", "application") == "resource":
                os.startfile(application["path"])
            else:
                command = [application["path"]]
                command.extend(application.get("arguments", []))
                process = subprocess.Popen(command)
                running_processes.append((application["name"], process))
            successful_launches += 1
        except OSError as e:
            launch_errors.append(f"Failed to open {application['name']}: {e}")

    if successful_launches > 0:
        active_workspace_name = workspace["name"]
        active_session.start()
    return successful_launches, launch_errors


def end_workspace() -> None:
    global active_workspace_name

    active_session.end()
    running_processes.clear()
    active_workspace_name = None


def request_application_close() -> list[str]:
    close_errors = []

    for name, process in running_processes:
        try:
            if process.poll() is not None:
                continue
            process.terminate()
        except OSError as e:
            close_errors.append(f"Failed to close {name}: {e}")

    return close_errors
