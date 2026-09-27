import requests
import logging
from config import APP_VERSION

logger = logging.getLogger(__name__)


def parse_version(version: str) -> tuple:
    clean_version = version.removeprefix("v")
    parts = clean_version.split(".")

    numbers = []
    for part in parts:
        numbers.append(int(part))

    return tuple(numbers)


def update_available(current_version: str, latest_version: str) -> bool:
    current_numbers = parse_version(current_version)
    latest_numbers = parse_version(latest_version)

    return latest_numbers > current_numbers


def get_latest_release(owner: str, repository: str) -> dict:
    api_url = f"https://api.github.com/repos/{owner}/{repository}/releases/latest"
    response = requests.get(api_url, timeout=10)
    response.raise_for_status()

    return response.json()


def check_for_updates(owner: str, repository: str) -> dict:
    try:
        release = get_latest_release(owner, repository)
        latest_version = release["tag_name"]
        release_url = release["html_url"]
        release_notes = release.get("body", "")

        if not isinstance(latest_version, str):
            raise ValueError("The release tag is not valid.")
        if not isinstance(release_url, str):
            raise ValueError("The release URL is not valid.")
        if not isinstance(release_notes, str):
            release_notes = ""

        available = update_available(APP_VERSION, latest_version)
    except (requests.RequestException, KeyError, TypeError, ValueError) as error:
        logger.warning("Update check failed: %s", error)
        return {
            "error": str(error),
        }

    result = {
        "available": available,
        "current_version": APP_VERSION,
        "latest_version": latest_version.removeprefix("v"),
        "release_url": release_url,
        "release_notes": release_notes,
    }

    return result
