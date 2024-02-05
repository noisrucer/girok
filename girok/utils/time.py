import calendar
from datetime import datetime, timedelta


def convert_iso_date_str_to_date_obj(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d")


def convert_date_obj_to_iso_date_str(date_obj: datetime) -> str:
    return date_obj.strftime("%Y-%m-%d")


def get_end_of_current_month_date() -> datetime:
    today = datetime.today()
    _, last_day = calendar.monthrange(today.year, today.month)
    end_date = convert_date_obj_to_iso_date_str(datetime(today.year, today.month, last_day))


def get_day_offset(dt1: datetime, dt2: datetime):
    dt1 = datetime.strptime(f"{dt1.year}-{dt1.month}-{dt1.day}", "%Y-%m-%d")
    dt2 = datetime.strptime(f"{dt2.year}-{dt2.month}-{dt2.day}", "%Y-%m-%d")
    diff = dt2 - dt1
    return diff.days


def build_date_info(dt: datetime):
    year, month, day = dt.year, dt.month, dt.day
    h, m, s = str(dt.time()).split(":")
    month_name = calendar.month_name[month]
    weekday_name = calendar.day_name[dt.weekday()]
    return f"{weekday_name}, {month_name} {day}, {year}"


def get_year_and_month_by_month_offset(month_offset: int, year=None, month=None):
    if year is None and month is None:
        now = datetime.now()
        year, month = now.year, now.month
    new_months = year * 12 + month + month_offset
    new_year = new_months // 12
    new_month = new_months % 12
    if new_month == 0:  # (1 - 1) % 12 = 0.
        new_year -= 1
        new_month = 12
    return new_year, new_month