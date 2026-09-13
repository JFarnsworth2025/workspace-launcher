import subprocess


def launch_workspace(workspace: dict) -> tuple[int, list[str]]:
    successful_launches = 0
    launch_errors = []

    for application in workspace["applications"]:
        try:
            command = [application["path"]]

            command.extend(application.get("arguments", []))

            subprocess.Popen(command)
            successful_launches += 1
        except OSError as e:
            launch_errors.append(f"Failed to launch {application['name']}: {str(e)}")

    return successful_launches, launch_errors
