import re
from datetime import datetime
from time import sleep
import typer
from rich import print
from rich.console import Console
from rich.table import Table
from rich.align import Align
from rich.padding import Padding
from rich.panel import Panel
from rich.layout import Layout

import constants as constants
from config import get_config
import api.task as task_api
import api.category as category_api
import utils.general as general_utils
import utils.display as display_utils
import utils.task as task_utils
import utils.auth as auth_utils
from rich.live import Live


app = typer.Typer(rich_markup_mode='rich')
console = Console()
layout = Layout()
cfg = get_config()

# Code Credits: https://github.com/tiangolo/typer/issues/140#issuecomment-898937671
def AddTaskDateMutuallyExclusiveGroup(size=2):
    group = set()
    def callback(ctx: typer.Context, param: typer.CallbackParam, value: str):
        # Add cli option to group if it was called with a value
        if value is not None and param.name not in group:
            group.add(param.name)
        if len(group) > size - 1:
            raise typer.BadParameter(f"{param.name} is mutually exclusive with {group.pop()}")
        return value
    return callback


def TimeMutuallyExclusiveGroup(size=2):
    time_group = set()
    def callback(ctx: typer.Context, param: typer.CallbackParam, value: str):
        # Add cli option to group if it was called with a value
        if value is not None and param.name not in time_group:
            time_group.add(param.name)
        if len(time_group) > size - 1:
            print(time_group)
            raise typer.BadParameter(f"{param.name} is mutually exclusive with {time_group.pop()}")
        return value
    return callback


def ShowTaskDateMutuallyExclusiveGroup(size=2):
    group = set()
    def callback(ctx: typer.Context, param: typer.CallbackParam, value: str):
        # Add cli option to group if it was called with a value
        if value is not None and param.name not in group:
            group.add(param.name)
        if len(group) > size - 1:
            raise typer.BadParameter(f"{param.name} is mutually exclusive with {group.pop()}")
        return value
    return callback


add_task_date_exclusivity_callback = AddTaskDateMutuallyExclusiveGroup()
time_exclusivity_callback = TimeMutuallyExclusiveGroup()
show_task_date_exclusivity_callback = ShowTaskDateMutuallyExclusiveGroup()
###################################################################################


def priority_callback(value: int):
    if value is None:
        return None
    
    if value < 1 or value > 5:
        raise typer.BadParameter("[Invalid priority] priority must be in [1, 5].")
    
    return value


def category_callback(ctx: typer.Context, param: typer.CallbackParam, value: str):
    command_name = ctx.command.name
    if value is None:
        return None

    if not re.match("^([a-zA-Z0-9]+/)*[a-zA-Z0-9]+/?$", value):
        raise typer.BadParameter("[Invalid category path] Category path must be in 'xx/yy/zz format.'")

    if value.endswith('/'):
        value = value[:-1]
        
    if command_name == "showtask" and value == 'none': # Show ALL tasks
        return value
    
    return value


def full_date_callback(ctx: typer.Context, param: typer.CallbackParam, value: str):
    command_name = ctx.command.name
    if command_name == "addtask":
        add_task_date_exclusivity_callback(ctx, param, value)
    elif command_name == "showtask":
        show_task_date_exclusivity_callback(ctx, param, value)
    
    if value is None:
        return None
    
    # "2023/02/23", "4/23"
    value = value.strip()
    args = value.split(" ")
    
    if len(args) != 1:
        raise typer.BadParameter("Deadline must be in 'yyyy/mm/dd' or 'mm/dd' format.")
    
    date = args[0]
    if not re.match("^([0-9]){4}/([0-9]){1,2}/([0-9]){1,2}|([0-9]){1,2}/([0-9]){1,2}$", date):
        raise typer.BadParameter("Deadline must be in 'yyyy/mm/dd' or 'mm/dd' format.")
    
    year, month, day = datetime.now().year, None, None
    date_list = list(map(int, date.split('/')))
    if len(date_list) == 3:
        year, month, day = date_list
    elif len(date_list) == 2:
        month, day = date_list
    
    if not task_utils.is_valid_year(year):
        raise typer.BadParameter(f"Invalid year: {year}. Year must be in [current_year - 3, current_year + 10]")
    if not task_utils.is_valid_month(month):
        raise typer.BadParameter(f"Invalid month: {month}")
    if not task_utils.is_valid_day(year, month, day):
        raise typer.BadParameter(f"Invalid day: {day}")
    
    return year, month, day


def time_callback(ctx: typer.Context, param: typer.CallbackParam, value: str):
    time_exclusivity_callback(ctx, param, value)
    if value is None:
        return None
    if not re.match("^[0-9]{2}:[0-9]{2}$", value):
        raise typer.BadParameter(f"[Invalid time: {value}. Time must be in hh:mm format.")
    
    hour, minute = value.split(':')
    if not task_utils.is_valid_hour(int(hour)):
        raise typer.BadParameter(f"Invalid hour: {hour}. Hour must be in [00-23].")
    if not task_utils.is_valid_minute(int(minute)):
        raise typer.BadParameter(f"Invalid minute: {minute}. Hour must be in [00-59].")
    
    return f"{hour}:{minute}:00"


def all_day_callback(ctx: typer.Context, param: typer.CallbackParam, value: bool):
    time_exclusivity_callback(ctx, param, value)
    if value is None:
        return False
    return value


def after_callback(ctx: typer.Context, param: typer.CallbackParam, value: int):
    add_task_date_exclusivity_callback(ctx, param, value)
    if value is None:
        return None

    if value <= 0:
        raise typer.BadParameter(f"Invalid offset: {value}. It must be greater than 0.")
    return value


def everyday_callback(value: bool):
    if value is None:
        return None
    return value


def offset_callback(ctx: typer.Context, param: typer.CallbackParam, value: int):
    command_name = ctx.command.name
    if command_name == "showtask":
        show_task_date_exclusivity_callback(ctx, param, value)
    if value is None:
        return None
    if value < 1:
        raise typer.BadParameter(f"Date offset must be greater or equal to 1.")
    if value > 1000:
        raise typer.BadParameter(f"Date offset is too big (must be greater than 0 and less than or equal to 1000)")
    return value
    

# Required: name, deadline
@app.command('addtask')
def add_task(
    name: str = typer.Argument(..., help="Task name"),
    cat: str = typer.Option(None, "-c", "--category", help="Category path - xx/yy/zz..", callback=category_callback),
    priority: int = typer.Option(None, "-p", "--priority", help="priority", callback=priority_callback),
    color: str = typer.Option(None, "--color", help="Color"),
    deadline: str = typer.Option(None, "-d", "--deadline", help="Deadline", callback=full_date_callback),
    everyday: bool = typer.Option(False, "-e", "--everyday", help="Set task due everyday"),
    today: bool = typer.Option(None, "--today", help="Set deadline to today", callback=add_task_date_exclusivity_callback),
    tomorrow: bool = typer.Option(None, "--tmr", "--tomorrow", help="Set deadline to tomorrow", callback=add_task_date_exclusivity_callback),
    this_mon: bool = typer.Option(None, "-t1", "--thismon", help="Set deadline to this Monday", callback=add_task_date_exclusivity_callback),
    this_tue: bool = typer.Option(None, "-t2", "--thistue", help="Set deadline to this Tuesday", callback=add_task_date_exclusivity_callback),
    this_wed: bool = typer.Option(None, "-t3", "--thiswed", help="Set deadline to, this Wednesday", callback=add_task_date_exclusivity_callback),
    this_thu: bool = typer.Option(None, "-t4", "--thisthu", help="Set deadline to this Thursday", callback=add_task_date_exclusivity_callback),
    this_fri: bool = typer.Option(None, "-t5", "--thisfri", help="Set deadline to this Friday", callback=add_task_date_exclusivity_callback),
    this_sat: bool = typer.Option(None, "-t6", "--thissat", help="Set deadline to this Saturday", callback=add_task_date_exclusivity_callback),
    this_sun: bool = typer.Option(None, "-t7", "--thissun", help="Set deadline to this Sunday", callback=add_task_date_exclusivity_callback),
    next_mon: bool = typer.Option(None, "-n1", "--nextmon", help="Set deadline to next Monday", callback=add_task_date_exclusivity_callback),
    next_tue: bool = typer.Option(None, "-n2", "--nexttue", help="Set deadline to next Tuesday", callback=add_task_date_exclusivity_callback),
    next_wed: bool = typer.Option(None, "-n3", "--nextwed", help="Set deadline to next Wednesday", callback=add_task_date_exclusivity_callback),
    next_thu: bool = typer.Option(None, "-n4", "--nextthu", help="Set deadline to next Thursday", callback=add_task_date_exclusivity_callback),
    next_fri: bool = typer.Option(None, "-n5", "--nextfri", help="Set deadline to next Friday", callback=add_task_date_exclusivity_callback),
    next_sat: bool = typer.Option(None, "-n6", "--nextsat", help="Set deadline to next Saturday", callback=add_task_date_exclusivity_callback),
    next_sun: bool = typer.Option(None, "-n7", "--nextsun", help="Set deadline to next Sunday", callback=add_task_date_exclusivity_callback),
    after: int = typer.Option(None, "-a", "--after", help="Set deadline to after x days", callback=after_callback),
    time: str = typer.Option(None, "-t", "--time", help="Deadline time, xx:yy", callback=time_callback),
    all_day: bool = typer.Option(None, "--allday", help="Set deadline time to all day", callback=all_day_callback),
    tag: str = typer.Option(None, "--tag", help="Tag"),
):  
    # Category
    cat_id = None
    if cat:
        cats = cat.split('/') if cat else []
        cat_id = category_api.get_last_cat_id(cats)
    
    # Deadline
    this_week_group = [this_mon, this_tue, this_wed, this_thu, this_fri, this_sat, this_sun]
    next_week_group = [next_mon, next_tue, next_wed, next_thu, next_fri, next_sat, next_sun]
    
    if not any(this_week_group + next_week_group + [deadline, today, tomorrow, after, everyday]):
        raise typer.BadParameter("At least one of deadline options is required.")
    
    if everyday and any(this_week_group + next_week_group + [deadline, today, tomorrow, after]):
        raise typer.BadParameter("'--everyday' option cannot be used with other deadline options.")
    
    year, month, day = None, None, None
    if deadline:
        year, month, day = deadline
        
    if today:
        year, month, day = task_utils.get_date_from_shortcut(True, datetime.now().weekday())
        
    if tomorrow:
        is_this_week = True
        weekday_num = datetime.now().weekday() + 1
        if weekday_num == 6:
            is_this_week = False
            weekday_num = 0
        year, month, day = task_utils.get_date_from_shortcut(is_this_week, weekday_num)
        
    if after:
        year, month, day = task_utils.get_date_from_offset(after)
    
    if any(this_week_group):
        this_week_day_num = [idx for idx, val in enumerate(this_week_group) if val][0]
        year, month, day = task_utils.get_date_from_shortcut(
            this_week=True,
            weekday_num=this_week_day_num
        )
        
    if any(next_week_group):
        this_week_day_num = [idx for idx, val in enumerate(next_week_group) if val][0]
        year, month, day = task_utils.get_date_from_shortcut(
            this_week=False,
            weekday_num=this_week_day_num
        )
    
    if everyday:
        year, month, day = "2000", "01", "01" # meaningless date in case of everyday
        
    full_deadline = f"{year}-{month}-{day} {time if time else '12:00:00'}"
    
    # Color - 만약 카테고리있으면 자동설정 (category 하고 Color 중복설정 불가)
    if cat:
        cat_color = category_api.get_category_color(cat_id)
        if color: # duplicate colors - prioritize default category color
            raise typer.BadParameter(f"\nInput color: {color}. However, you have set the color for {cat} as {cat_color}.")
        color = cat_color
    else:
        if not color: # default color
            color = constants.DEFAULT_TASK_COLOR
            
    task_data = {
        "task_category_id": cat_id,
        "name": name,
        "deadline": full_deadline,
        "priority": priority,
        "color": color,
        "everyday": everyday,
        "tag": tag,
        "all_day": all_day,
        "is_time": time is not None
    }
    resp = task_api.create_task(task_data)
    
    if resp.status_code == 201:
        display_utils.center_print("Task added successfully!", constants.DISPLAY_TERMINAL_COLOR_SUCCESS)
        tasks_resp = task_api.get_tasks()
        tasks = general_utils.bytes2dict(tasks_resp.content)['tasks']
        task_tree = display_utils.display_tasks_by_category(tasks)
        current_date = task_utils.build_date_info(datetime.now())
        display_utils.center_print(current_date, constants.DISPLAY_TERMINAL_COLOR_TITLE)
        print(task_tree)
        
    elif resp.status_code == 400:
        err_msg = general_utils.bytes2dict(resp.content)['detail']
        display_utils.center_print(err_msg, constants.DISPLAY_TERMINAL_COLOR_ERROR)
    else:
        display_utils.center_print("Error occurred.", constants.DISPLAY_TERMINAL_COLOR_ERROR)
    
    
@app.command("showtask")
def show_task(
    cat: str = typer.Option(None, "-c", "--category", help="Category path - xx/yy/zz..", callback=category_callback),
    exact_day: str = typer.Option(None, "-e", "--exact", help="Deadline", callback=full_date_callback),
    within_days: int = typer.Option(None, "-d", "--day", help="Show tasks due within the specified days", callback=offset_callback),
    within_weeks: int = typer.Option(None, "-w", "--week", help="Show tasks due within the specified weeks", callback=offset_callback),
    within_months: int = typer.Option(None, "-m", "--month", help="Show tasks due within the specified months", callback=offset_callback),
    today: bool = typer.Option(None, "-t", "--tdy", help="Show tasks due today", callback=show_task_date_exclusivity_callback),
    within_tomorrow: bool = typer.Option(None, "--tmr", help="Show tasks due today and tomorrow", callback=show_task_date_exclusivity_callback),
    within_this_week: bool = typer.Option(None, "--tw", "--thisweek", help="Show tasks due within this week", callback=show_task_date_exclusivity_callback),
    within_next_week: bool = typer.Option(None, "--nw", "--nextweek", help="Show tasks due within next week", callback=show_task_date_exclusivity_callback),
    within_this_month: bool = typer.Option(None, "--tm", "--thismonth", help="Show tasks due within this month", callback=show_task_date_exclusivity_callback),
    within_next_month: bool = typer.Option(None, "--nm", "--nextmonth", help="Show tasks due within next month", callback=show_task_date_exclusivity_callback),
    this_mon: bool = typer.Option(None, "-t1", "--thismon", help="Show tasks due exactly this Monday", callback=show_task_date_exclusivity_callback),
    this_tue: bool = typer.Option(None, "-t2", "--thistue", help="Show tasks due exactly this Tuesday", callback=show_task_date_exclusivity_callback),
    this_wed: bool = typer.Option(None, "-t3", "--thiswed", help="Show tasks due exactly this Wednesday", callback=show_task_date_exclusivity_callback),
    this_thu: bool = typer.Option(None, "-t4", "--thisthu", help="Show tasks due exactly this Thursday", callback=show_task_date_exclusivity_callback),
    this_fri: bool = typer.Option(None, "-t5", "--thisfri", help="Show tasks due exactly this Friday", callback=show_task_date_exclusivity_callback),
    this_sat: bool = typer.Option(None, "-t6", "--thissat", help="Show tasks due exactly this Saturday", callback=show_task_date_exclusivity_callback),
    this_sun: bool = typer.Option(None, "-t7", "--thissun", help="Show tasks due exactly this Sunday", callback=show_task_date_exclusivity_callback),
    next_mon: bool = typer.Option(None, "-n1", "--nextmon", help="Show tasks due exactly next Monday", callback=show_task_date_exclusivity_callback),
    next_tue: bool = typer.Option(None, "-n2", "--nexttue", help="Show tasks due exactly next Tuesday", callback=show_task_date_exclusivity_callback),
    next_wed: bool = typer.Option(None, "-n3", "--nextwed", help="Show tasks due exactly next Wednesday", callback=show_task_date_exclusivity_callback),
    next_thu: bool = typer.Option(None, "-n4", "--nextthu", help="Show tasks due exactly next Thursday", callback=show_task_date_exclusivity_callback),
    next_fri: bool = typer.Option(None, "-n5", "--nextfri", help="Show tasks due exactly next Friday", callback=show_task_date_exclusivity_callback),
    next_sat: bool = typer.Option(None, "-n6", "--nextsat", help="Show tasks due exactly next Saturday", callback=show_task_date_exclusivity_callback),
    next_sun: bool = typer.Option(None, "-n7", "--nextsun", help="Show tasks due exactly next Sunday", callback=show_task_date_exclusivity_callback),
    urgent: bool = typer.Option(None, "-u", "--urgent", help="Show urgent tasks (due within 3 days)", callback=show_task_date_exclusivity_callback),
    priority: int = typer.Option(None, "-p", "--priority", help="Show tasks of the given priority"),
    tag: str = typer.Option(None, "--tag", help="Show tasks belonging to the given tag"),
    tree_view: bool = typer.Option(None, "--tree", help="Show tasks with tree view"),
):
    # (1) Category - if None, show ALL categories (including "None" category)
    # To show "None" category, user must provide explicitly
    if cat is None: # ALL categories
        cats = None
    elif cat == 'none': # "None" category
        cats = ['']
    else:
        cats = cat.split('/')
    
    # (2) Date: start_date, end_date
    start_date, end_date = None, None
    
    this_week_group = [this_mon, this_tue, this_wed, this_thu, this_fri, this_sat, this_sun]
    next_week_group = [next_mon, next_tue, next_wed, next_thu, next_fri, next_sat, next_sun]
    
    if exact_day:
        print(exact_day)
    
    if today is not None:
        start_date, end_date = task_utils.build_time_window_by_day_offsets(0, 0)
        
    if within_tomorrow is not None:
        start_date, end_date = task_utils.build_time_window_by_day_offsets(0, 1)

    if within_days is not None:
        start_date, end_date = task_utils.build_time_window_by_day_offsets(0, within_days)
    
    if within_weeks is not None:
        start_date, end_date = task_utils.build_time_window_by_day_offsets(0, 7 * within_weeks)
        
    if within_months is not None: # 
        start_date, end_date = task_utils.build_time_window_by_month_offset(within_months)
        
    if within_this_week is not None:
        # 오늘이 ex. 수요일이라도 이번주 월~일 다 보여주기
        current_weekday_num = task_utils.get_current_weekday_num()
        start_date, end_date = task_utils.build_time_window_by_day_offsets(-current_weekday_num, 6 - current_weekday_num)
        
    if within_next_week is not None:
        current_weekday_num = task_utils.get_current_weekday_num()
        start_date, end_date = task_utils.build_time_window_by_day_offsets(-current_weekday_num, 6 - current_weekday_num + 7)
        
    if within_this_month is not None:
        start_date, end_date = task_utils.build_current_month_time_window()
        
    if within_next_month is not None:
        start_date, end_date = task_utils.build_time_window_by_month_offset(1)
    
    if urgent:
        today_ = task_utils.get_date_from_offset(0)
        three_days_after_ = task_utils.get_date_from_offset(3)
        start_date, end_date = task_utils.build_time_window([*today_], [*three_days_after_])
    
    if any(this_week_group):
        this_week_day_num = [idx for idx, val in enumerate(this_week_group) if val][0]
        year, month, day = task_utils.get_date_from_shortcut(
            this_week=True,
            weekday_num=this_week_day_num
        )
        start_date, end_date = task_utils.build_time_window([year, month, day], [year, month, day])
        
    if any(next_week_group):
        this_week_day_num = [idx for idx, val in enumerate(next_week_group) if val][0]
        year, month, day = task_utils.get_date_from_shortcut(
            this_week=False,
            weekday_num=this_week_day_num
        )
        start_date, end_date = f"{year}-{month}-{day} 00:00:00", f"{year}-{month}-{day} 11:59:59"

    resp = task_api.get_tasks(
        cats=cats,
        start_date=start_date,
        end_date=end_date,
        min_pri=priority,
        max_pri=priority,
        tag=tag
    )
    
    if resp.status_code == 200:
        tasks = general_utils.bytes2dict(resp.content)['tasks']
        task_tree = display_utils.display_tasks_by_category(tasks)
        current_date = task_utils.build_date_info(datetime.now())
        display_utils.center_print(current_date, constants.DISPLAY_TERMINAL_COLOR_TITLE)
        print(task_tree)

    elif resp.status_code == 400:
        err_msg = general_utils.bytes2dict(resp.content)['detail']
        display_utils.center_print(err_msg, constants.DISPLAY_TERMINAL_COLOR_ERROR)
    else:
        display_utils.center_print("Error occurred.", constants.DISPLAY_TERMINAL_COLOR_ERROR)
    
    
@app.command("showtag")
def show_tag():
    resp = task_api.get_tags()
    if resp.status_code == 200:
        tags = general_utils.bytes2dict(resp.content)['tags']
        for tag in tags:
            print(tag)
    elif resp.status_code == 400:
        err_msg = general_utils.bytes2dict(resp.content)['detail']
        display_utils.center_print(err_msg, constants.DISPLAY_TERMINAL_COLOR_ERROR)
    else:
        print(resp)