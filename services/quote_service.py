import json
import requests
import logging
from datetime import date
from config import QUOTE_CACHE_FILE
from services.json_service import save_json

DEFAULT_QUOTE = {
    "date": "",
    "quote": (
        "To be yourself in a world that is constantly trying to make you "
        "something else is the greatest accomplishment."
    ),
    "author": "Ralph Waldo Emerson",
}

logger = logging.getLogger(__name__)


def get_daily_quotes() -> dict:

    cache = DEFAULT_QUOTE.copy()

    if QUOTE_CACHE_FILE.exists():
        try:
            with QUOTE_CACHE_FILE.open("r", encoding="utf-8") as file:
                cache = json.load(file)
        except (ValueError, OSError, TypeError) as error:
            logger.warning("Could not load the quote cache: %s", error)

    if not isinstance(cache, dict):
        cache = DEFAULT_QUOTE.copy()
    if not isinstance(cache.get("quote"), str) or not isinstance(cache.get("author"), str):
        cache = DEFAULT_QUOTE.copy()

    today = str(date.today())

    if (
        cache.get("date") == today
        and isinstance(cache.get("quote"), str)
        and isinstance(cache.get("author"), str)
    ):
        return {"quote": cache["quote"], "author": cache["author"]}

    try:
        response = requests.get("https://zenquotes.io/api/random", timeout=5)
        response.raise_for_status()
        quote = response.json()[0]
        if not isinstance(quote["q"], str) or not isinstance(quote["a"], str):
            raise ValueError("The quote response must contain quote and author text.")
    except (requests.RequestException, ValueError, KeyError, IndexError, TypeError) as error:
        logger.info("Daily Quote request was unavailable: %s", error)
        return {"quote": cache["quote"], "author": cache["author"]}

    cache = {
        "date": today,
        "quote": quote["q"],
        "author": quote["a"],
    }

    try:
        save_json(QUOTE_CACHE_FILE, cache)
    except OSError as error:
        logger.warning("Could not save the quote cache: %s", error)

    return {"quote": cache["quote"], "author": cache["author"]}
