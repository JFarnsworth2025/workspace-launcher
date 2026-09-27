import datetime


def get_time_based_greeting(author: str) -> str:
    current_hour = datetime.datetime.now().hour

    if 0 <= current_hour < 12:
        return f"Good Morning {author}"
    elif 12 <= current_hour < 18:
        return f"Good Afternoon {author}"
    else:
        return f"Good Evening {author}"
