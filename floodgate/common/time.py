from random import randint
import re
from typing import Type, TypeVar

import pendulum as pen
import pytimeparse

__all__ = [
    "parse_time",
    "parse_duration",
    "random_time",
]

time_pattern = re.compile(
    r"^"
    r"(?P<hour>[0-2]?\d)"
    r"(?::?(?P<minute>\d{2}))?"
    r"\s*"
    r"(?:(?P<period_am>a|am)|(?P<period_pm>p|pm))?"
    r"$",
    re.I,
)


V = TypeVar("V")


def parse_time(time_str: str, class_: Type[V] = pen.Time) -> V:
    """
    Parse a string as a time specifier of the general format "12:34 PM".

    :return: the parsed time
    """

    match = time_pattern.match(time_str)
    if not match:
        raise ValueError("No match")

    hour = int(match["hour"])
    minute = int(match["minute"] or 0)

    if (0 > hour > 23) or (0 > minute > 59):
        raise ValueError("Hour or minute is out of range")

    if match["period_pm"]:
        if hour < 12:
            # This is PM and we use 24 hour times in datetime, so add 12 hours
            hour += 12
        elif hour == 12:
            # 12 PM is 12:00
            pass
        else:
            raise ValueError("24 hour times do not use AM or PM")
    elif match["period_am"]:
        if hour < 12:
            # AM, so no change
            pass
        elif hour == 12:
            # 12 AM is 00:00
            hour = 0
        else:
            raise ValueError("24 hour times do not use AM or PM")

    return class_(hour, minute)


def parse_duration(duration_str: str, class_: Type[V] = pen.Duration) -> V:
    seconds = pytimeparse.parse(duration_str)
    if seconds is None:
        raise ValueError("Invalid time duration")
    return class_(seconds=seconds)


def random_time(start: pen.Time, end: pen.Time) -> pen.Time:
    if end < start:
        raise ValueError("end must be a time after start")
    hour = randint(start.hour, end.hour)
    minute = randint(start.minute, end.minute)
    second = randint(start.second, end.second)
    return pen.time(hour, minute, second)
