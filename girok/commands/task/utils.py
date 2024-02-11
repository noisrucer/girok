import re
from datetime import date, datetime, timedelta
from typing import Callable, List, Tuple

import typer

from girok.constants import EVENT_IDS_CACHE_PATH
from girok.utils.json_utils import read_json, write_json


def decode_date_format(date_str: str) -> Tuple[bool, str]:
    """Decode date input into ISO date format, 'yyyy-mm-dd'.

    Args:
        date_str (str): The input date string for `-d` command option.

    Returns:
        Tuple[bool, str]: is_success, ISO date format('yyyy-mm-dd')
    """
    decode_functions: List[Callable[[str], Tuple[bool, str]]] = [
        decode_direct_date_format,
        decode_this_week_date_format,
        decode_next_week_date_format,
        decode_after_date_format,
        decode_today_date_format,
        decode_tomorrow_date_format,
    ]

    for decode_func in decode_functions:
        valid, iso_date_str = decode_func(date_str)
        if valid:
            return True, iso_date_str

    return False, None


def decode_direct_date_format(date_str: str) -> Tuple[bool, str]:
    """
    date_str: 2024/05/26, 2024/5/26, 05/26, 5/26
    """
    is_matched = bool(re.match("^([0-9]){4}/([0-9]){1,2}/([0-9]){1,2}|([0-9]){1,2}/([0-9]){1,2}$", date_str))

    if not is_matched:
        return False, None

    date_items = [int(i) for i in date_str.split("/")]
    year, month, day = datetime.now().year, None, None
    if len(date_items) == 3:
        year, month, day = date_items
    elif len(date_items) == 2:
        month, day = date_items
    else:
        raise ValueError("Invalid date_str format")

    try:
        iso_date_str = to_iso_date_str(year, month, day)
        return True, iso_date_str
    except ValueError:
        return False, None


def decode_this_week_date_format(date_str: str) -> Tuple[bool, str]:
    """
    date_str: t1, t2, ..., t7
    """
    if date_str not in ["t1", "t2", "t3", "t4", "t5", "t6", "t7"]:
        return False, None

    today = date.today()
    monday = today - timedelta(days=today.weekday())

    delta = int(date_str[1]) - 1
    target = monday + timedelta(days=delta)
    year, month, day = target.year, target.month, target.day
    try:
        iso_date_str = to_iso_date_str(year, month, day)
        return True, iso_date_str
    except ValueError:
        return False, None


def decode_next_week_date_format(date_str: str) -> Tuple[bool, str]:
    """
    date_str: n1, n2, ..., n7
    """
    if date_str not in ["n1", "n2", "n3", "n4", "n5", "n6", "n7"]:
        return False, None

    today = date.today()
    next_monday = today - timedelta(days=today.weekday()) + timedelta(days=7)
    delta = int(date_str[1]) - 1
    target = next_monday + timedelta(days=delta)
    year, month, day = target.year, target.month, target.day
    try:
        iso_date_str = to_iso_date_str(year, month, day)
        return True, iso_date_str
    except ValueError:
        return False, None


def decode_after_date_format(date_str: str) -> Tuple[bool, str]:
    """
    date_str: a1, a10, a50, ...
    """
    is_matched = bool(re.match("^a[1-9]\d*$", date_str))
    if not is_matched:
        return False, None
    delta = int(date_str[1:])
    target = date.today() + timedelta(days=delta)
    year, month, day = target.year, target.month, target.day
    try:
        iso_date_str = to_iso_date_str(year, month, day)
        return True, iso_date_str
    except ValueError:
        return False, None


def decode_today_date_format(date_str: str) -> Tuple[bool, str]:
    """
    date_str: tdy, today
    """
    if date_str not in ["tdy", "today"]:
        return False, None

    target = date.today()
    year, month, day = target.year, target.month, target.day
    try:
        iso_date_str = to_iso_date_str(year, month, day)
        return True, iso_date_str
    except ValueError:
        return False, None


def decode_tomorrow_date_format(date_str: str) -> Tuple[bool, str]:
    """
    date_str: tmr, tomorrow
    """
    if date_str not in ["tmr", "tomorrow"]:
        return False, None

    target = date.today() + timedelta(days=1)
    year, month, day = target.year, target.month, target.day
    try:
        iso_date_str = to_iso_date_str(year, month, day)
        return True, iso_date_str
    except ValueError:
        return False, None


def decode_time_format(time_str: str) -> Tuple[bool, str]:
    is_matched = bool(re.match("^[01][0-9]|2[0-3]:[0-5][0-9]$", time_str))
    if not is_matched:
        return False, None

    return True, time_str + ":00"


def to_iso_date_str(year: int, month: int, day: int) -> str:
    return date(year, month, day).strftime("%Y-%m-%d")


def validate_start_end_window(start_date: str, start_time: str, end_date: str, end_time: str) -> bool:
    if start_date and not start_time and not end_date and not end_time:
        # start_date
        return True, None
    elif start_date and start_time and not end_date and not end_time:
        # start_date, start_time
        return True, None
    elif start_date and not start_time and end_date and not end_time:
        # start_date, end_date
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        if end <= start:
            return False, "End date must be greater than start date"
        return True, None
    elif start_date and start_time and end_date and end_time:
        # start_date, start_time, end_date, end_time
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        start_time = datetime.strptime(start_time, "%H:%M:%S").time()
        start = datetime.combine(start_date, start_time)

        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        end_time = datetime.strptime(end_time, "%H:%M:%S").time()
        end = datetime.combine(end_date, end_time)

        if end <= start:
            return False, "End date must be greater than start date"
        return True, None
    else:
        return (
            False,
            "Only allowed combinations are (1)start_date, (2)start_date, start_time, (3)start_date, end_date, (4)start_date, start_time, end_date, end_time",
        )


def cache_event_ids(event_ids_cache: dict):
    write_json(EVENT_IDS_CACHE_PATH, event_ids_cache)


def get_event_ids_cache():
    try:
        cache = read_json(EVENT_IDS_CACHE_PATH)
    except:
        raise typer.Exit()
    return cache
