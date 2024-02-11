from rich.style import Style
from rich.text import Text
from textual import events, log
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.messages import Message
from textual.reactive import reactive, var
from textual.widget import Widget
from textual.widgets import Button, Footer, Header, Label, Placeholder, Static, Tree
from textual.widgets._tree import TreeNode

import girok.calendar_cli.utils as calendar_utils
import girok.api.category as category_api
import girok.api.task as task_api
from girok.constants import CATEGORY_COLOR_PALETTE, Emoji
from girok.calendar_cli.entity import Category



class CategoryTree(Tree):
    CSS_PATH = "./demo_dock.css"
    categories: list[dict] = None
    can_focus = True
    can_focus_children = True
    auto_expand = False
    highlighted_node = None
    selected_node = None
    init_select = False
    init_highlight = False

    class CategoryChanged(Message):
        def __init__(self, category: Category):
            super().__init__()
            self.category = category

    class CustomTestMessage(Message):
        def __init__(self):
            super().__init__()

    def on_mount(self):
        self.highlighted_node = self.root
        self.selected_node = self.root
        calendar_utils.add_left_arrow_tree(self.highlighted_node)

        self.line = 0
        resp = category_api.get_all_categories()
        if not resp.is_success:
            exit(0)
        self.categories = resp.body['rootCategories']
        self.root.expand()

        for category in self.categories:
            top_cat = self.root.add(
                category['name'], expand=True, data={"color": category['color'], "id": category['id']}
            )
            top_cat.allow_expand = True
            calendar_utils.build_category_tree(top_cat, category['children'])

    def on_key(self, evt):
        if evt.key == "j":
            self.action_cursor_down()
        elif evt.key == "k":
            self.action_cursor_up()
        elif evt.key == "o":
            self.action_select_cursor()

    def render_label(self, node, base_style: Style, style: Style):
        node_label = node._label.copy()
        icon = ""
        if node.parent is None:
            icon = "📖 "
        elif node.parent.parent is None:
            icon = Text("● ", style=CATEGORY_COLOR_PALETTE[node.data["color"]])
        text = Text()
        text.append(icon)
        text.append(node_label)
        return text

    def on_tree_node_selected(self, event: Tree.NodeSelected):
        event.stop()
        full_cat_path = calendar_utils.get_full_path_from_node(event.node)
        self.selected_node = event.node
        if full_cat_path == "":
            category = Category(id=None, path="")
        else:
            category = Category(id=event.node.data['id'], path=full_cat_path)
        self.post_message(self.CategoryChanged(category))

    def on_tree_node_highlighted(self, event: Tree.NodeHighlighted):
        event.stop()
        prev_highlighted_node = self.highlighted_node
        calendar_utils.remove_left_arrow_tree(prev_highlighted_node)
        calendar_utils.remove_highlight(prev_highlighted_node)
        calendar_utils.add_left_arrow_tree(event.node)
        calendar_utils.add_highlight(event.node)
        self.highlighted_node = event.node

    def on_focus(self, evt):
        calendar_utils.add_left_arrow_tree(self.highlighted_node)


class TagTree(Tree):
    CSS_PATH = "./demo_dock.css"
    tags = []
    can_focus = True
    can_focus_children = True
    auto_expand = False
    highlighted_node = None
    selected_node = None

    class TagChanged(Message):
        def __init__(self, tag: str):
            super().__init__()
            self.tag = tag

    class CustomTestMessage(Message):
        def __init__(self):
            super().__init__()

    def on_mount(self):
        self.select_node(self.root)
        self.action_select_cursor()
        self.highlighted_node = self.root
        self.selected_node = self.root

        # tags = task_api.get_tags()
        resp = task_api.get_all_tags()
        if not resp.is_success:
            exit(0)
        self.tags = resp.body['tags']
        self.root.expand()

        for tag in self.tags:
            self.root.add(tag, expand=True)

    def on_key(self, evt):
        if evt.key == "j":
            self.action_cursor_down()
        elif evt.key == "k":
            self.action_cursor_up()
        elif evt.key == "o":
            self.action_select_cursor()

    def on_focus(self, evt):
        calendar_utils.add_left_arrow_tree(self.highlighted_node)

    def render_label(self, node, base_style: Style, style: Style):
        node_label = node._label.copy()

        icon = ""
        if node.parent is None:
            icon = "📖 "
        elif node.parent.parent is None:
            icon = Text("● ", style="white")

        text = Text()
        text.append(icon)
        text.append(node_label)
        return text

    def on_tree_node_selected(self, event: Tree.NodeSelected):
        event.stop()
        tag = str(event.node._label)
        if tag.endswith(" " + Emoji.LEFT_ARROW):
            tag = tag[:-2]

        self.post_message(self.TagChanged(tag))
        self.selected_node = event.node

    def on_tree_node_highlighted(self, event: Tree.NodeHighlighted):
        event.stop()
        prev_highlighted_node = self.highlighted_node
        calendar_utils.remove_highlight(prev_highlighted_node)
        calendar_utils.remove_left_arrow_tree(prev_highlighted_node)
        calendar_utils.add_left_arrow_tree(event.node)
        calendar_utils.add_highlight(event.node)
        self.highlighted_node = event.node


class SidebarMainContainer(Vertical):
    CSS_PATH = "./demo_dock.css"

    def compose(self):
        yield CategoryTree("All Categories", id="sidebar")
        yield TagTree("All Tags", id="tag-tree")


class SidebarContainer(Vertical):
    CSS_PATH = "./demo_dock.css"

    def compose(self):
        yield SidebarMainContainer(id="sidebar-main-container")
