from rich.style import Style
from rich.table import Table
from textual import log
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.messages import Message
from textual.widget import Widget
from textual.widgets import Button, Footer, Header, Label, Placeholder, Static, Tree

import girok.api.category as category_api
import girok.calendar_cli.utils as calendar_utils
from girok.calendar_cli.calendar_container import CalendarContainer
from girok.calendar_cli.sidebar import CategoryTree, SidebarContainer
from girok.calendar_cli.entity import Category
from girok.constants import Emoji

class CalendarApp(Horizontal):
    CSS_PATH = "./demo_dock.css"

    def compose(self):
        yield SidebarContainer(id="sidebar-container")
        yield CalendarContainer(id="calendar-container")

    def on_category_tree_category_changed(self, event: CategoryTree.CategoryChanged):
        self.query_one(CalendarContainer).update_category(event.category)
        cat_tree = self.query_one(CategoryTree)

    def on_tag_tree_tag_changed(self, event):
        tag = event.tag
        if tag.endswith(" " + Emoji.LEFT_ARROW):
            tag = tag[:-2]
        if tag == "All Tags":
            tag = None
        self.query_one(CalendarContainer).update_tag(tag)

    def on_category_tree_custom_test_message(self, event):
        self.refresh()
