from datetime import datetime, timedelta
from calendar import monthrange
import calendar

def is_valid_year(year: int):
    if year < datetime.now().year - 3 or year > datetime.now().year + 10:
        return False
    return True
    
    
def is_valid_month(month: int):
    if month <= 0 or month > 12:
        return False
    return True


def is_valid_day(year: int, month: int, day: int):
    if day not in range(1, monthrange(year, month)[1] + 1):
        return False
    return True


def is_valid_hour(hour: int):
    if hour < 0 or hour > 23:
        return False
    return True


def is_valid_minute(minute: int):
    if minute < 0 or minute > 59:
        return False
    return True


def get_date_from_shortcut(this_week: bool, weekday_num: int):
    """
    Params:
        - this_week (bool): True if this week, False if next week
        - weekday_num (int): 0 ~ 6, referring to monday ~ sunday
    """
    if not this_week:
        weekday_num += 7
        
    current_weekday_num = datetime.now().weekday()
    day_offset = weekday_num - current_weekday_num
    deadline_date = datetime.now() + timedelta(days=day_offset)
    
    return deadline_date.year, deadline_date.month, deadline_date.day


def get_date_from_offset(offset: int):
    deadline_date = datetime.now() + timedelta(days=offset)
    return deadline_date.year, deadline_date.month, deadline_date.day


def get_today_date():
    now = datetime.now()
    return now.year, now.month, now.day

def get_last_day_of_current_month():
    now = datetime.now()
    return monthrange(now.year, now.month)[1]


def build_time_window(start: list, end: list):
    """
    start (list): [year, month, day]
    end (list): [year, month, day]
    """
    start_date, end_date = f"{start[0]}-{start[1]}-{start[2]} 00:00:00", f"{end[0]}-{end[1]}-{end[2]} 11:59:59" 
    return start_date, end_date


def build_time_window_by_day_offsets(start_offset: int, end_offset: int):
    start = get_date_from_offset(start_offset)
    end = get_date_from_offset(end_offset)
    return build_time_window([*start], [*end])


def build_time_window_by_month_offset(month_offset: int):
    now = datetime.now()
    current_year, current_month = now.year, now.month
    new_year, new_month = get_year_and_month_by_month_offset(month_offset)
    start_date = f"{current_year}-{current_month}-01 00:00:00"
    last_day_of_end_month = monthrange(new_year, new_month)[1]
    end_date = f"{new_year}-{new_month}-{last_day_of_end_month} 11:59:59"
    return start_date, end_date


def build_current_month_time_window():
    now = datetime.now()
    year, month = now.year, now.month
    start_date = f"{year}-{month}-01 00:00:00"
    last_day_of_current_month = get_last_day_of_current_month()
    end_date = f"{year}-{month}-{last_day_of_current_month} 11:59:59"
    return start_date, end_date


def build_time_window_by_year_and_month(year=None, month=None):
    start_date = f"{year}-{month}-01 00:00:00"
    last_day_of_current_month = monthrange(year, month)[1]
    end_date = f"{year}-{month}-{last_day_of_current_month} 11:59:59"
    return start_date, end_date
    

def get_year_and_month_by_month_offset(month_offset: int, year=None, month=None):
    if year is None and month is None:
        now = datetime.now()
        year, month = now.year, now.month
    new_months = (year * 12 + month + month_offset)
    new_year = new_months // 12
    new_month = new_months % 12
    if new_month == 0: # (1 - 1) % 12 = 0.
        new_year -= 1
        new_month = 12
    return new_year, new_month


def get_current_weekday_num():
    now = datetime.now()
    current_weekday_num = now.weekday()
    return current_weekday_num


def get_weekday_name_from_date(year, month, day, abbr=True):
    time = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d")
    if abbr:
        return calendar.day_abbr[time.weekday()]
    else:
        return calendar.day_name[time.weekday()]


def get_month_name_from_month(month: int, abbr=True):
    if abbr:
        return get_month_name_by_number(month, abbr=True)
    else:
        return get_month_name_by_number(month, abbr=False)


def build_date_info(dt: datetime):
    year, month, day = dt.year, dt.month, dt.day
    h, m, s = str(dt.time()).split(":")
    month_name = get_month_name_from_month(month, abbr=True)
    weekday_name = get_weekday_name_from_date(year, month, day, abbr=False)
    return f"{weekday_name}, {month_name} {day}, {year}"


def get_day_offset_between_two_dates(dt1, dt2):
    dt1 = datetime.strptime(f"{dt1.year}-{dt1.month}-{dt1.day}", "%Y-%m-%d")
    dt2 = datetime.strptime(f"{dt2.year}-{dt2.month}-{dt2.day}", "%Y-%m-%d")
    diff = dt2 - dt1
    return diff.days

def get_month_name_by_number(month_num: int, abbr=False):
    """
    month_num: 0 ~ 11
    """
    if abbr:
        return calendar.month_abbr[month_num]
    else:
        return calendar.month_name[month_num]