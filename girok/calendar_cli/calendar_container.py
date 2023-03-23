import asyncio
from datetime import datetime, timedelta
import calendar

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Static, Label, Placeholder, Tree, DataTable
from textual.messages import Message
from textual.widget import Widget
from textual.reactive import var
from rich.text import Text
from rich.style import Style
from rich.segment import Segment
from rich.panel import Panel
from rich.markdown import Markdown
from textual import log

import girok.api.task as task_api
import girok.api.category as category_api
import girok.utils.calendar as calendar_utils
import girok.utils.general as general_utils
import girok.utils.task as task_utils
import girok.constants as constants
from girok.calendar_cli.sidebar import CategoryTree, TagTree


class WeekdayBarContainer(Horizontal):
    pass

class CalendarHeader(Vertical):
    year = datetime.now().year
    month = datetime.now().month
    cat_path = ""
    tag = ""

    def on_mount(self):
        self.display_date()

    def compose(self):
        month_name = task_utils.get_month_name_by_number(self.month)

        with Horizontal():
            with Container(id="calendar-header-category-container"):
                yield Static(self.cat_path, id="calendar-header-category")
            with Container(id="calendar-header-date-container"):
                yield Static(Text(f"{month_name} {self.year}", style=Style(color=constants.CALENDAR_HEADER_DATE_COLOR, bold=True)), id="calendar-header-date")
            with Container(id="calendar-header-tag-container"):
                yield Static(f"{self.tag}", id="calendar-header-tag")
        yield Horizontal()
        with WeekdayBarContainer(id="weekday-bar"):
            yield Static(Text("Monday", style=Style(color=constants.CALENDAR_WEEKDAY_NAME_COLOR, bold=True)), classes="calendar-weekday-name")
            yield Static(Text("Tuesday", style=Style(color=constants.CALENDAR_WEEKDAY_NAME_COLOR, bold=True)), classes="calendar-weekday-name")
            yield Static(Text("Wednesday", style=Style(color=constants.CALENDAR_WEEKDAY_NAME_COLOR, bold=True)), classes="calendar-weekday-name")
            yield Static(Text("Thursday", style=Style(color=constants.CALENDAR_WEEKDAY_NAME_COLOR, bold=True)), classes="calendar-weekday-name")
            yield Static(Text("Friday", style=Style(color=constants.CALENDAR_WEEKDAY_NAME_COLOR, bold=True)), classes="calendar-weekday-name")
            yield Static(Text("Saturday", style=Style(color="#87C5FA", bold=True)), classes="calendar-weekday-name")
            yield Static(Text("Sunday", style=Style(color="#DB4455", bold=True)), classes="calendar-weekday-name")

    def update_year_and_month(self, year, month):
        self.year, self.month = year, month
        self.display_date()

    def update_cat_path(self, new_cat_path):
        self.cat_path = new_cat_path
        self.display_date()

    def update_tag(self, new_tag):
        self.tag = new_tag
        self.display_date()

    def display_date(self):
        month_name = task_utils.get_month_name_by_number(self.month, abbr=False)
        calendar_header_category = self.query_one("#calendar-header-category")
        calendar_header_date = self.query_one("#calendar-header-date")
        calendar_header_tag = self.query_one("#calendar-header-tag")
        calendar_weekday_bar = self.query_one("#weekday-bar")

        calendar_header_category.update(Text(f"Category: /{self.cat_path}", style=Style(color=constants.CALENDAR_HEADER_DATE_COLOR)))
        calendar_header_date.update(Text(f"{month_name} {self.year}", style=Style(color=constants.CALENDAR_HEADER_DATE_COLOR, bold=True)))
        calendar_header_tag.update(Text(f"Tag: {self.tag}", style=Style(color=constants.CALENDAR_HEADER_DATE_COLOR)))


class CalendarCell(Vertical):
    pass


class Calendar(Container):
    year = datetime.now().year
    month = datetime.now().month
    cat_path = "" # If "", show all categories
    tag = ""
    tasks = []
    can_focus = True
    cur_month_first_day_cell_num = None
    cur_focused_cell_cord = (None, None)
    cur_focused_cell = None
    m = 5
    n = 7
    grid = [[False for _ in range(7)] for _ in range(5)]
    is_pop_up = False

    class TaskCellSelected(Message):
        def __init__(self, cell_tasks, year, month, day):
            super().__init__()
            self.cell_tasks = cell_tasks
            self.year = year
            self.month = month
            self.day = day

    def on_mount(self):
        self.update_calendar()

    def compose(self):
        for i in range(35):
            yield CalendarCell(classes="calendar-cell", id=f"cell{i}")

    def on_key(self, event):
        if self.is_pop_up:
            return
        x, y = self.cur_focused_cell_cord
        if event.key == 'h': # left
            next_cell_coord = (x, y - 1)
        elif event.key == 'j': # down
            next_cell_coord = (x + 1, y)
        elif event.key == 'k': # up
            next_cell_coord = (x - 1, y)
        elif event.key == 'l': # right
            next_cell_coord = (x, y + 1)
        elif event.key == 'o':
            pass
        else:
            return

        if event.key in ['h', 'j', 'k', 'l']: # moving on cells
            nx, ny = next_cell_coord
            if nx < 0 or ny < 0 or nx >= self.m or ny >= self.n: # Out of matrix
                return

            if not self.grid[nx][ny]: # Out of boundary of the current month
                return

            prev_cell_num = calendar_utils.convert_coord_to_cell_num(*self.cur_focused_cell_cord)
            prev_cell = self.query_one(f"#cell{prev_cell_num}")
            calendar_utils.remove_left_arrow(prev_cell)

            cur_cell_num = calendar_utils.convert_coord_to_cell_num(nx, ny)
            next_cell = self.query_one(f"#cell{cur_cell_num}")
            calendar_utils.add_left_arrow(next_cell)

            self.cur_focused_cell_cord = (nx, ny)
            self.cur_focused_cell = next_cell
        elif event.key == 'o': # select a cell
            cur_cell_num = calendar_utils.convert_coord_to_cell_num(x, y)
            cur_cell = self.query_one(f"#cell{cur_cell_num}")
            cell_tasks = cur_cell.children[1:] # task data

            # Retrieve tasks for the selected day
            selected_day = calendar_utils.convert_cell_num_to_day(self.year, self.month, cur_cell_num)
            cell_tasks = list(filter(
                lambda x: calendar_utils.get_date_obj_from_str_separated_by_T(x['deadline']).day == selected_day,
                self.tasks
            ))
            self.post_message(self.TaskCellSelected(cell_tasks, self.year, self.month, selected_day))
            self.is_pop_up = True

    def on_focus(self):
        x, y = calendar_utils.convert_cell_num_to_coord(self.cur_month_first_day_cell_num)
        target_cell = self.query_one(f"#cell{self.cur_month_first_day_cell_num}")
        # target_cell.add_class("focused-cell")
        calendar_utils.add_left_arrow(target_cell)
        self.cur_focused_cell_cord = (x, y)
        self.cur_focused_cell = target_cell

    def update_year_and_month(self, year, month):
        self.year, self.month = year, month
        self.update_calendar()

    def update_cat_path(self, new_cat_path: str):
        self.cat_path = new_cat_path
        self.update_calendar(show_arrow=False)

    def update_tag(self, new_tag: str):
        self.tag = new_tag
        self.update_calendar(show_arrow=False)

    def refresh_cell_days(self):
        self.grid = [[False for _ in range(7)] for _ in range(5)]
        first_weekday, total_days = calendar.monthrange(self.year, self.month)
        self.cur_month_first_day_cell_num = first_weekday
        now = datetime.now()
        for i in range(35):
            cell = self.query_one(f"#cell{i}")
            for child in cell.walk_children():
                child.remove()
            if i >= first_weekday and i <= first_weekday + total_days - 1:
                x, y = calendar_utils.convert_cell_num_to_coord(i)
                self.grid[x][y] = True
                day = calendar_utils.convert_cell_num_to_day(self.year, self.month, i)
                day_text = Text()
                day_text.append(f"{day}")
                if self.year == now.year and self.month == now.month and day == now.day:
                    day_text = Text(str(day_text), style=Style(bgcolor=constants.CALENDAR_TODAY_COLOR, color="black"))
                    # day_text.stylize(style=Style(bgcolor=constants.CALENDAR_TODAY_COLOR, color="black"))
                cell.mount(Label(day_text, id=f"cell-header-{i}"))

    def update_calendar(self, show_arrow=True):
        """
        If val == "", then "root category" is selected
        """
        if self.cat_path == "": # all categories
            cat_list = None
        elif self.cat_path == "No Category":
            cat_list = ['']
        else:
            cat_list = self.cat_path[:-1].split('/')

        if self.tag == "":
            tag = None
        else:
            tag = self.tag
            
        log("CATS", cat_list),
        log("tag", tag)

        start_date, end_date = task_utils.build_time_window_by_year_and_month(self.year, self.month)
        resp = task_api.get_tasks(
            cats=cat_list,
            start_date=start_date,
            end_date=end_date,
            tag=tag,
            view="list"
        )

        if resp.status_code == 200:
            self.refresh_cell_days()
            tasks = general_utils.bytes2dict(resp.content)['tasks']
            self.tasks = tasks
            first_weekday, last_day = calendar.monthrange(self.year, self.month)

            if self.cur_focused_cell:
                if show_arrow:
                    calendar_utils.remove_left_arrow(self.cur_focused_cell)
                self.cur_focused_cell_cord = calendar_utils.convert_cell_num_to_coord(first_weekday)
                self.cur_focused_cell = self.query_one(f"#cell{first_weekday}") # update
                if show_arrow:
                    calendar_utils.add_left_arrow(self.cur_focused_cell)

            for idx, task in enumerate(tasks):
                full_date = task['deadline']
                day = datetime.strptime(full_date, "%Y-%m-%dT%H:%M:%S").day
                cell_num = calendar_utils.convert_day_to_cell_num(self.year, self.month, day)
                cell = self.query_one(f"#cell{cell_num}")
                color = task['color']
                name = task['name']
                # if len(name) > 13:
                #     name = name[:13] + ".."
                task_item_name = Text()
                task_item_name.append("●", style=constants.CIRCLE_COLOR[color])
                task_item_name.append(" " + name)

                task_item = Static(task_item_name, id=f"task-cell{cell_num}-{idx}", classes="task-item")
                cell.mount(task_item)

                task_item = self.query_one(f"#task-cell{cell_num}-{idx}")
                task_item.styles.overflow_x = "hidden"
                task_item.styles.overflow_y = "hidden"

        elif resp.status_code == 400:
            err_msg = general_utils.bytes2dict(resp.content)['detail']
            exit(0)
        else:
            exit(0)


class CalendarContainer(Vertical):
    year = datetime.now().year
    month = datetime.now().month
    cat_path = None # If none, show all categories
    tag = None

    def update_month_by_offset(self, offset: int):
        new_year, new_month = task_utils.get_year_and_month_by_month_offset(
            month_offset=offset,
            year=self.year,
            month=self.month
        )
        self.year, self.month = new_year, new_month
        calendar_header = self.query_one(CalendarHeader)
        cal = self.query_one(Calendar)

        calendar_header.update_year_and_month(self.year, self.month)
        cal.update_year_and_month(self.year, self.month)

    def update_year_and_month(self, year: int, month: int):
        self.year, self.month = year, month
        calendar_header = self.query_one(CalendarHeader)
        cal = self.query_one(Calendar)

        calendar_header.update_year_and_month(self.year, self.month)
        cal.update_year_and_month(self.year, self.month)

    def update_cat_path(self, cat_path: str):
        """
        cat_path: ex) HKU/COMP3230 or ""
        """
        self.cat_path = cat_path
        cal = self.query_one(Calendar)
        cal.update_cat_path(new_cat_path=cat_path)

        cal_header = self.query_one(CalendarHeader)
        cal_header.update_cat_path(new_cat_path=cat_path)


    def update_tag(self, tag: str):
        self.tag = tag
        cal = self.query_one(Calendar)
        cal.update_tag(new_tag=tag)
        cal_header = self.query_one(CalendarHeader)
        cal_header.update_tag(new_tag=tag)


    def compose(self):
        yield CalendarHeader(id="calendar-header")
        yield Calendar(id="calendar")
