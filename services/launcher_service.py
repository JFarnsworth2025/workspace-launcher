import os
import subprocess

running_processes: list[tuple[str, subprocess.Popen]] = []


def get_running_applications() -> list[str]:
    running_processes[:] = [
        (name, process) for name, process in running_processes if process.poll() is None
    ]
    return [name for name, _ in running_processes]


def launch_workspace(workspace: dict) -> tuple[int, list[str]]:
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

    return successful_launches, launch_errors
