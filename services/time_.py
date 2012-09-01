import datetime
from datetime import date, timedelta


DAYS = {"monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6}
# Three-letter day prefixes:
DAYS.update(dict((k[:3], v) for k, v in DAYS.items()))

UNITS = {"week": timedelta(days=7),
         "month": timedelta(weeks=4),
         "year": timedelta(weeks=52)}

THIS_UNITS = {"week": timedelta(days=3),
              "month": timedelta(weeks=2),
              "year": timedelta(weeks=26)}

SUFFIXES = {"morning": timedelta(hours=6),
            "afternoon": timedelta(hours=12),
            "noon": timedelta(hours=12),
            "evening": timedelta(hours=18),
            "night": timedelta(hours=21)}


def get_datetime(when="now"):
    if when == "now":
        return datetime.now()

    # TODO: This should handle things like "three weeks"

    # We want a datetime, but we only want the date half
    today = date.today()
    today = datetime.datetime(year=today.year, month=today.month, day=today.day)

    if when == "today":
        return today

    pieces = when.split(" ")

    if pieces[-1] in SUFFIXES:
        return get_datetime(" ".join(pieces[:-1])) + SUFFIXES[pieces[-1]]
    
    TIME_DELTAS = {"this": today,
                   "last": today + timedelta(days=-1),
                   "tomorrow": today + timedelta(days=1),
                   "yesterday": today + timedelta(days=-1),
                   "tonight": today + SUFFIXES["night"]}
    if when in TIME_DELTAS:
        return TIME_DELTAS[when]

    if pieces[0] == "next":
        remaining_pieces = " ".join(pieces[1:])
        # Handle "next week", "next month"
        if remaining_pieces in SUFFIXES:
            return today + SUFFIXES[remaining_pieces]
        elif remaining_pieces in UNITS:
            return today + UNITS[remaining_pieces]

        # Handle "next tuesday", "next thursday"
        return get_datetime(" ".join(remaining_pieces))

    # Handle "this tuesday", "this week"
    if pieces[0] == "this" and len(pieces) > 1:
        remaining_pieces = " ".join(pieces[1:])
        if remaining_pieces in THIS_UNITS:
            return today + THIS_UNITS[remaining_pieces]
        return get_datetime(remaining_pieces)

    if when in DAYS:
        seeking_dow = DAYS[when]
        dow = today.weekday()
        if dow >= seeking_dow:
            return today + timedelta(days=7 - (dow - seeking_dow))
        else:
            return today + timedelta(days=seeking_dow - dow)

    return today
