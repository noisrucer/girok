from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Static, Label, Placeholder, Tree
from textual.messages import Message
from textual.widget import Widget

import girok.api.category as category_api
import girok.utils.calendar as calendar_utils
from rich.table import Table
from rich.style import Style
from textual import log

from girok.calendar_cli.sidebar import SidebarContainer, CategoryTree
from girok.calendar_cli.calendar_container import CalendarContainer
import girok.constants as constants
        
class CalendarApp(Horizontal):
    CSS_PATH = "./demo_dock.css"
    
    def compose(self):
        yield SidebarContainer(id="sidebar-container")
        yield CalendarContainer(id="calendar-container")
                
    def on_category_tree_category_changed(self, event):
        self.query_one(CalendarContainer).update_cat_path(event.cat_path)
        cat_tree = self.query_one(CategoryTree)
        
    def on_tag_tree_tag_changed(self, event):
        tag = event.tag
        if tag.endswith(" " + constants.LEFT_ARROW_EMOJI):
            tag = tag[:-2]
        if tag == "All Tags":
            tag = ""
        self.query_one(CalendarContainer).update_tag(tag)
        
    def on_category_tree_custom_test_message(self, event):
        self.refresh()