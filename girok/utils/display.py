from datetime import datetime
import calendar

from rich import print
from rich.console import Console
from rich.tree import Tree
from rich.align import Align
from rich import box
from rich.style import Style
from rich.table import Table, Column
from rich.text import Text
from rich.align import Align
import shutil

import girok.utils.task as task_utils
import girok.utils.calendar as calendar_utils
import girok.utils.general as general_utils
from girok.config import get_config
import girok.constants as constants

console = Console()
cfg = get_config()

def display_categories(cats_dict: dict, highlight_cat=None):
    tree = Tree("")
    for idx, cat in enumerate(cats_dict):
        display_category(
            cats_dict,
            cat,
            top_most=True,
            tree=tree,
            cumul_path=cat,
            highlight_cat=highlight_cat,
            color=cats_dict[cat]['color']
        )
    console.print(tree)
    
    
def display_category(
    cats_dict: dict,
    cat: str,
    top_most=True,
    tree: Tree=None,
    cumul_path="",
    highlight_cat=None,
    color=None,
):
    style = Style(
        color=constants.TABLE_HEADER_COLOR if highlight_cat != cumul_path else "#B9D66A",
        bold=True
    )
        
    # if top_most:
    circle = Text(constants.CIRCLE_EMOJI + " ", style=Style(color=constants.CIRCLE_COLOR[color]))
        
    dir_name = Text(f"{cat}", style=style)
    # if top_most:
    dir_name = Text.assemble(circle, dir_name)
        
    tree = tree.add(dir_name)
    for sub in cats_dict[cat]['subcategories'].keys():
        display_category(
            cats_dict[cat]['subcategories'],
            sub,
            top_most=False,
            tree=tree,
            cumul_path=cumul_path + "/" + sub,
            highlight_cat=highlight_cat,
            color=color
        )
        
    
def center_print(text, type: str = None, wrap: bool = False):
    if type == "title":
        style = Style(
            color=constants.DISPLAY_TERMINAL_COLOR_TITLE_TEXT,
            bgcolor=constants.DISPLAY_TERMINAL_COLOR_TITLE_BACKGROUND
        )
    elif type == "success":
        style = Style(
            color=constants.DISPLAY_TERMINAL_COLOR_SUCCESS_TEXT,
            bgcolor=constants.DISPLAY_TERMINAL_COLOR_SUCCESS_BACKGROUND
        )
    elif type == "error":
        style = Style(
            color=constants.DISPLAY_TERMINAL_COLOR_ERROR_TEXT,
            bgcolor=constants.DISPLAY_TERMINAL_COLOR_ERROR_BACKGROUND
        )
    elif type == "warning":
        style = Style(
            color=constants.DISPLAY_TERMINAL_COLOR_WARNING_TEXT,
            bgcolor=constants.DISPLAY_TERMINAL_COLOR_WARNING_BACKGROUND 
        )
    else:
        style = Style(
            color=constants.DISPLAY_TERMINAL_COLOR_TITLE_TEXT,
            bgcolor=constants.DISPLAY_TERMINAL_COLOR_TITLE_BACKGROUND
        )
    if wrap:
        width = shutil.get_terminal_size().columns // 2
    else:
        width = shutil.get_terminal_size().columns
        
    content = Text(text, style=style)
    console.print(Align.center(content, style=style, width=width), height=100)
    
    
def display_tasks_by_category(
    task_tree,
    color_dict,
    marked_task_id: int = None,
    marked_color: str = constants.TABLE_TASK_DELETED_COLOR
):
    # print(task_tree)
    task_ids_cache = {}
    tree = Tree("")
    for idx, cat_name in enumerate(task_tree):
        tree.add(display_category_with_tasks(
            cat_name=cat_name,
            task_tree=task_tree[cat_name],
            color_dict=color_dict,
            top_most=True,
            task_ids_cache=task_ids_cache,
            marked_task_id=marked_task_id,
            marked_color=marked_color
            ))
    general_utils.cache_task_ids(cfg=cfg, cache=task_ids_cache)
    return tree


def display_category_with_tasks(
    cat_name,
    task_tree: dict,
    color_dict,
    top_most,
    task_ids_cache,
    marked_task_id: int = None,
    marked_color: str = constants.TABLE_TASK_DELETED_COLOR,
):
    dir_name = Text(f"{cat_name}", style=Style(color=constants.TABLE_HEADER_COLOR, bold=True))
    dir_name = Text.assemble(
        Text(f"{constants.CIRCLE_EMOJI} ", style=Style(color=constants.CIRCLE_COLOR[color_dict[cat_name]])),
        dir_name
    )
        
    tree = Tree(dir_name)
    
    for sub_cat_name in task_tree['sub_categories']:
        sub_tree = display_category_with_tasks(
            cat_name=sub_cat_name,
            task_tree=task_tree['sub_categories'][sub_cat_name],
            color_dict=color_dict,
            top_most=False,
            task_ids_cache=task_ids_cache,
            marked_task_id=marked_task_id,
            marked_color=marked_color
        )
        tree.add(sub_tree)
        
    for task in task_tree['tasks']:
        # Cache task id
        if not(task['task_id'] == marked_task_id and marked_color == constants.TABLE_TASK_DELETED_COLOR):
            task_ids_cache[len(task_ids_cache) + 1] = task['task_id']
        
        deadline = datetime.strptime(task['deadline'], "%Y-%m-%dT%H:%M:%S")
        year, month, day = deadline.year, deadline.month, deadline.day
        h, m, s = str(deadline.time()).split(":")
        
        weekday_name = task_utils.get_weekday_name_from_date(year, month, day)
        
        h = int(h)
        is_time = task['is_time']
        afternoon = h >= 12
        if h > 12:
            h -= 12
            
        time = f" {h}:{m} {'PM' if afternoon else 'AM'} " if is_time else ' '
        remaining_days = task_utils.get_day_offset_between_two_dates(datetime.now(), deadline)
        day_offset_message = f"{remaining_days} days left" if remaining_days > 0 else f"{abs(remaining_days)} days passed"
        
        if remaining_days == 0:
            day_offset_message = "Due Today"
            
        if not(task['task_id'] == marked_task_id and marked_color == constants.TABLE_TASK_DELETED_COLOR):
            task_id = Text(f"[{len(task_ids_cache)}] ", style=Style(color="white" if task['task_id'] != marked_task_id else marked_color))
        else:
            task_id = ""
        task_name = Text(task['name'], style=Style(color=constants.TABLE_TASK_NAME_COLOR  if task['task_id'] != marked_task_id else marked_color, bold=True))
        task_remaining_days = Text(f" [{day_offset_message}]", style=Style(color='#F5F7F2' if task['task_id'] != marked_task_id else marked_color))
        task_date = Text(f" - {year}/{month}/{day}{time}{weekday_name}", style=Style(color="white" if task['task_id'] != marked_task_id else marked_color))
        node_name = Text.assemble(task_id, task_name, task_remaining_days, task_date, style=Style(strike=True if task['task_id'] == marked_task_id and marked_color == constants.TABLE_TASK_DELETED_COLOR else False))
             
        tree.add(node_name)
        
    return tree        
            
            
def display_tasks_by_list(tasks: list, marked_task_id: int = None, color: str = constants.TABLE_TASK_DELETED_COLOR):
    table = build_task_table(tasks, marked_task_id, color)
    print(Align(table, align="center"))
    
    
def build_task_table(tasks: list, marked_task_id: int = None, color: str = constants.TABLE_TASK_DELETED_COLOR):
    tasks = sorted(tasks, key=lambda x: calendar_utils.get_date_obj_from_str_separated_by_T(x['deadline']))
    num_tasks = len(tasks)
    table = Table(
        Column(header="ID", justify="center", header_style=Style(color=constants.TABLE_HEADER_COLOR), style=Style(color=constants.TABLE_TASK_NAME_COLOR)),
        Column(header="Name", header_style=Style(color=constants.TABLE_HEADER_COLOR), style=Style(color=constants.TABLE_TASK_NAME_COLOR)),
        Column(header="Category", justify="center", header_style=Style(color=constants.TABLE_HEADER_COLOR), style=Style(color=constants.TABLE_TEXT_COLOR)),
        Column(header="Deadline", justify="center", header_style=Style(color=constants.TABLE_HEADER_COLOR), style=Style(color="green")),
        Column(header="Time", justify="center", header_style=Style(color=constants.TABLE_HEADER_COLOR), style=Style(color=constants.TABLE_TEXT_COLOR)),
        Column(header="Tag", justify="center", header_style=Style(color=constants.TABLE_HEADER_COLOR), style=Style(color=constants.TABLE_TEXT_COLOR)),
        Column(header="Priority", justify="center", header_style=Style(color=constants.TABLE_HEADER_COLOR), style=Style(color=constants.TABLE_TEXT_COLOR)),
        Column(header="Remaining", justify="center", header_style=Style(color=constants.TABLE_HEADER_COLOR), style=Style(color=constants.TABLE_TEXT_COLOR)),
        box=box.SIMPLE_HEAVY,
        show_lines=False if num_tasks > 15 else True,
        border_style=Style(color="#D7E1C9", bold=True)
    )
    
    task_ids_cache = {}
    for idx, task in enumerate(tasks):
        # Cache task id
        task_ids_cache[idx + 1] = task['task_id']
        
        date = calendar_utils.get_date_obj_from_str_separated_by_T(task['deadline'])
        deadline = f"{date.day} {calendar.month_name[date.month]} {date.year}"
        h, m, s = str(date.time()).split(":")
        h = int(h)
        is_time = task['is_time']
        afternoon = h >= 12
        if h > 12:
            h -= 12
        time = f"{h}:{m} {'PM' if afternoon else 'AM'}" if is_time else '-'
        
        remaining_days = task_utils.get_day_offset_between_two_dates(datetime.now(), date)
        day_offset_message = f"{remaining_days} days left" if remaining_days > 0 else f"{abs(remaining_days)} days passed"
        if remaining_days == 0:
            day_offset_message = "Due Today"
        circle = Text(constants.CIRCLE_EMOJI + " ", style=Style(color=constants.CIRCLE_COLOR[task['color']]))
        task_name = Text.assemble(circle, task['name'], style=Style(color=color if marked_task_id == task['task_id'] else constants.TABLE_TASK_NAME_COLOR, bold=True))
        
        table.add_row(
            Text(str(idx + 1), style=Style(color=color if marked_task_id == task['task_id'] else constants.TABLE_TEXT_COLOR)),
            task_name,
            Text(task['task_category_full_path'] if task['task_category_full_path'] else "None", style=Style(color=color if marked_task_id == task['task_id'] else constants.TABLE_TEXT_COLOR)),
            Text(deadline, style=Style(color=color if marked_task_id == task['task_id'] else constants.TABLE_DEADLINE_COLOR)),
            Text(time, style=Style(color=color if marked_task_id == task['task_id'] else constants.TABLE_DEADLINE_COLOR)),
            Text(task['tag'] if task['tag'] else '-', style=Style(color=color if marked_task_id == task['task_id'] else constants.TABLE_TEXT_COLOR)),
            Text(str(task['priority']) if task['priority'] else '-', style=Style(color=color if marked_task_id == task['task_id'] else constants.TABLE_TEXT_COLOR)),
            Text(day_offset_message, style=Style(color=color if marked_task_id == task['task_id'] else constants.TABLE_TEXT_COLOR))
        )
    
    general_utils.cache_task_ids(cfg=cfg, cache=task_ids_cache)
        
    return table
    

    
    

    
