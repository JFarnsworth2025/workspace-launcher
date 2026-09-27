import json
import requests
import logging
from datetime import date
from config import VERSES_FILE

with VERSES_FILE.open("r", encoding="utf-8") as file:
    DAILY_VERSES = json.load(file)

logger = logging.getLogger(__name__)


def get_today_reference() -> dict:
    index = date.today().toordinal() % len(DAILY_VERSES)

    return DAILY_VERSES[index]


def get_daily_verse() -> dict:
    reference = get_today_reference()
    reference_label = (
        f"{reference['book']} {reference['chapter']}:"
        f"{reference['start_verse']}-{reference['end_verse']}"
    )

    url = (
        f"https://bible.helloao.org/api/"
        f"BSB/"
        f"{reference['book']}/"
        f"{reference['chapter']}.json"
    )

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        chapter = response.json()
    except (requests.RequestException, ValueError, KeyError) as error:
        logger.info("Daily verse request was unavailable: %s", error)
        return {
            "reference": reference_label,
            "text": "Today's verse is unavailable while offline.",
        }

    try:
        verses = []

        for item in chapter["chapter"]["content"]:
            if item["type"] != "verse":
                continue

            verse_number = item["number"]

            if (
                verse_number < reference["start_verse"]
                or verse_number > reference["end_verse"]
            ):
                continue

            parts = [piece for piece in item["content"] if isinstance(piece, str)]
            verses.append(f"{verse_number}. {' '.join(parts)}")

        if not verses:
            raise ValueError("The verse response did not contain the requested verses.")

        return {
            "reference": (
                f"{chapter['book']['name']} "
                f"{reference['chapter']}:"
                f"{reference['start_verse']}"
                f"-{reference['end_verse']}"
            ),
            "text": "\n".join(verses),
        }
    except (KeyError, TypeError, ValueError) as error:
        logger.warning("Daily verse response could not be read: %s", error)
        return {
            "reference": reference_label,
            "text": "Today's verse is unavailable while offline.",
        }
