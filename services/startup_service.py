from pathlib import Path
import sys
import winreg

APP_NAME = "Workspace Launcher"


def get_startup_command() -> str:
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'

    python = Path(sys.executable).with_name("pythonw.exe")
    script = Path(__file__).resolve().parent.parent / "main.py"

    return f'"{python}" "{script}"'


def enable_startup() -> None:

    command = get_startup_command()

    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0,
        winreg.KEY_SET_VALUE,
    )

    try:
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, command)
    finally:
        winreg.CloseKey(key)


def disable_startup() -> None:
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        )

        try:
            winreg.DeleteValue(key, APP_NAME)
        finally:
            winreg.CloseKey(key)

    except FileNotFoundError:
        pass


def sync_startup(enabled: bool) -> None:
    if enabled:
        enable_startup()
    else:
        disable_startup()
