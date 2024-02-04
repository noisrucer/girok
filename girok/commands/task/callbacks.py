import re
from datetime import datetime
from typing import Optional

import typer

from girok.commands.task.utils import decode_date_format, decode_time_format
from girok.constants import REPETITION_TYPE, TASK_PRIORITY


def allow_empty_category_callback(ctx: typer.Context, param: typer.CallbackParam, value: str):
    if value is None:
        return None

    if value == "/":
        return value.rstrip("/")

    if not re.match("^([a-zA-Z0-9]+/)*[a-zA-Z0-9]+/?$", value):
        raise typer.BadParameter("[Invalid category path] Category path must be in 'xx/yy/zz format.'")

    if value.endswith("/"):
        value = value[:-1]

    if value == "none":
        raise typer.BadParameter("Sorry, 'none' is a reserved category name.")
    return value


def not_allow_empty_category_callback(ctx: typer.Context, param: typer.CallbackParam, value: str):
    if value is None:
        return None

    if not re.match("^([a-zA-Z0-9]+/)*[a-zA-Z0-9]+/?$", value):
        raise typer.BadParameter("[Invalid category path] Category path must be in 'xx/yy/zz format.'")

    if value.endswith("/"):
        value = value[:-1]

    if value == "none":
        raise typer.BadParameter("Sorry, 'none' is a reserved category name.")
    return value


def datetime_callback(ctx: typer.Context, param: typer.CallbackParam, value: str):
    if value is None:
        return None
    """
    Check if
    1. xxx
    2. xxx@yyy
    """
    if "@" not in value:
        valid, iso_date_str = decode_date_format(value)
        if not valid:
            raise typer.BadParameter("Invalid date format")
        return iso_date_str, None
    else:
        date_items = value.split("@")
        if len(date_items) != 2:
            raise typer.BadParameter("Invalid date format")
        date_str, time_str = date_items

        # Validate date
        valid, iso_date_str = decode_date_format(date_str)
        if not valid:
            raise typer.BadParameter("Invalid date format")

        # Validate time
        valid, iso_time_str = decode_time_format(time_str)
        if not valid:
            raise typer.BadParameter("Invalid time format")

        return iso_date_str, iso_time_str


def tags_callback(ctx: typer.Context, param: typer.CallbackParam, value: Optional[str]):
    if value is None:
        return None
    is_matched = bool(re.match("^[^,]+(,[^,]+)*$", value))
    if not is_matched:
        raise typer.BadParameter("Invalid tags format. You must specify tags separated by comma such as 'A,B,C'")
    return value


def priority_callback(ctx: typer.Context, param: typer.CallbackParam, value: str):
    if value is None:
        return None

    if value not in TASK_PRIORITY:
        raise typer.BadParameter("Priority must be one of 'low', 'medium', 'high'")

    return TASK_PRIORITY[value]


def date_callback(ctx: typer.Context, param: typer.CallbackParam, value: str):
    if value is None:
        return None

    valid, iso_date_str = decode_date_format(value)
    if not valid:
        raise typer.BadParameter("Invalid date format")
    return iso_date_str


def valid_integer_callback(ctx: typer.Context, param: typer.CallbackParam, value: int):
    if value is None:
        return None

    if value <= 0:
        raise typer.BadParameter("The time window must be a positive integer")

    return value
