from datetime import datetime
import calendar

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Static, Label, Placeholder, Tree
from textual.widget import Widget
from textual.messages import Message
from textual import log
from textual.reactive import var, reactive
from textual.pilot import Pilot
from rich.text import Text
from rich.table import Table
from rich.style import Style
from rich import box
from rich.table import Column

import girok.api.category as category_api
import girok.utils.calendar as calendar_utils
import girok.utils.display as display_utils

from girok.calendar_cli.calendar_app import CalendarApp
from girok.calendar_cli.calendar_container import CalendarContainer, Calendar
from girok.calendar_cli.sidebar import CategoryTree, SidebarContainer, TagTree
import girok.constants as constants


class Entry(App):
    CSS_PATH = "./calendar_main.css"
    current_focused = "CategoryTree"
    is_pop_up = False
    BINDINGS = [
        ("q", "quit", "Quit Nuro"),
        ("u", "show_previous_month", "Show prev month"),
        ("i", "show_next_month", "Show next month"),
        ("y", "show_current_month", "Show current month"),
        ("e", "focus_on_calendar", "Move to calendar"),
        ("w", "focus_on_sidebar", "Move to sidebar"),
        ("ctrl+j", "move_down_to_tag_tree", "Move down to tag tree"),
        ("ctrl+k", "move_up_to_category_tree", "Move up to category tree"),
        ("o", 'close_pop_up', "Close pop up box"),
        ("f", "toggle_files", "Toggle Files")
    ]
    show_sidebar = reactive(True)
    pilot = None
    
    def on_mount(self):
        self.set_focus(self.query_one(CategoryTree))
        
    def compose(self):
        yield CalendarApp()
        # yield Footer()
        
    # Display pop-up box when selecting a cell
    def on_calendar_task_cell_selected(self, event: Calendar.TaskCellSelected):
        cell_tasks = event.cell_tasks
        year, month, day = event.year, event.month, event.day
        table = display_utils.build_task_table(cell_tasks)
        
        self.query_one(CalendarContainer).mount(
            Vertical(
                Static(Text(f"{day} {calendar.month_name[month]} {year}", style=Style(bold=True, color=constants.TABLE_HEADER_DATE_COLOR)), classes="task-pop-up-header"),
                Container(Static(table, classes="task-pop-up-table"), classes="task-pop-up-table-container"),
                classes='task-pop-up-container',
            )
        )
        self.is_pop_up = True
        
    def action_quit(self):
        self.exit()
       
    def action_show_next_month(self):
        if self.is_pop_up:
            return
        calendar_container = self.query_one(CalendarContainer)
        calendar_container.update_month_by_offset(1)
         
    def action_show_previous_month(self):
        if self.is_pop_up:
            return
        calendar_container = self.query_one(CalendarContainer)
        calendar_container.update_month_by_offset(-1)
        
    def action_show_current_month(self):
        if self.is_pop_up:
            return
        calendar_container = self.query_one(CalendarContainer)
        now = datetime.now()
        cur_year, cur_month = now.year, now.month
        calendar_container.update_year_and_month(cur_year, cur_month)
        
    def action_focus_on_calendar(self):
        if self.is_pop_up:
            return
        self.set_focus(self.query_one(Calendar))
        self.current_focused = "Calendar"
        
        cat_tree = self.query_one(CategoryTree)
        tag_tree = self.query_one(TagTree)
        calendar_utils.remove_left_arrow_tree(cat_tree.highlighted_node)
        calendar_utils.remove_left_arrow_tree(tag_tree.highlighted_node)
        calendar_utils.remove_highlight(cat_tree.highlighted_node)
        calendar_utils.remove_highlight(tag_tree.highlighted_node)
        
    def action_focus_on_sidebar(self):
        if self.is_pop_up:
            return
        self.set_focus(self.query_one(CategoryTree))
        self.current_focused = "CategoryTree"
        
        cal = self.query_one(Calendar)
        
        # self.pilot.hover(Calendar)
        
        if self.is_pop_up:
            return
        
        cat_tree = self.query_one(CategoryTree)
        calendar_utils.remove_left_arrow(cal.cur_focused_cell)
        calendar_utils.add_highlight(cat_tree.highlighted_node)
        
        ############# UNKNOWN ERROR - Temporary Fix ############
        ngbrs = [self.query_one("#cell0"), self.query_one("#cell1"), self.query_one("#cell2"), self.query_one("#cell3"), self.query_one("#cell4"), self.query_one("#cell5"), self.query_one("#cell6")]
        for ngbr_cell in ngbrs:
            temp = []
            while ngbr_cell.children:
                child = ngbr_cell.children[0]
                temp.append(child.render())
                child.remove()
                
            for child in temp:
                ngbr_cell.mount(Static(child))
        ######################################################
        
    def action_move_down_to_tag_tree(self):
        if self.is_pop_up:
            return
        if self.current_focused != "CategoryTree":
            return
        tag_tree = self.query_one(TagTree)
        self.set_focus(tag_tree)
        self.current_focused = "TagTree"
        category_tree = self.query_one(CategoryTree)
        calendar_utils.remove_highlight(category_tree.highlighted_node)
        calendar_utils.remove_left_arrow_tree(category_tree.highlighted_node)
        calendar_utils.add_left_arrow_tree(tag_tree.highlighted_node)
        calendar_utils.add_highlight(tag_tree.highlighted_node)
    
    def action_move_up_to_category_tree(self):
        if self.is_pop_up:
            return
        if self.current_focused != "TagTree":
            return
        category_tree = self.query_one(CategoryTree)
        self.set_focus(category_tree)
        self.current_focused = "CategoryTree"
        tag_tree = self.query_one(TagTree)
        calendar_utils.remove_highlight(tag_tree.highlighted_node)
        calendar_utils.remove_left_arrow_tree(tag_tree.highlighted_node)
        calendar_utils.add_left_arrow_tree(category_tree.highlighted_node)
        calendar_utils.add_highlight(category_tree.highlighted_node)
        
    def action_close_pop_up(self):
        if not self.is_pop_up:
            return
        self.query_one(".task-pop-up-container").remove()
        self.query_one(Calendar).is_pop_up = False
        self.is_pop_up = False
        
    def action_toggle_files(self):
        self.show_sidebar = not self.show_sidebar
        sidebar_container = self.query_one(SidebarContainer)
        if self.show_sidebar:
            sidebar_container.styles.display = "block"
        else:
            sidebar_container.styles.display = "none"
            
            
if __name__ == '__main__':
   app = Entry()
   app.run()