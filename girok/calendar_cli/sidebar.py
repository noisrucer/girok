from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Static, Label, Placeholder, Tree
from textual.messages import Message
from textual.widget import Widget
from textual.reactive import var, reactive
from textual import events

import girok.api.category as category_api
import girok.api.task as task_api
import girok.utils.calendar as calendar_utils
import girok.utils.general as general_utils
import girok.constants as constants
from rich.style import Style
from rich.text import Text
from textual import log
from textual.widgets._tree import TreeNode

class CategoryTree(Tree):
    CSS_PATH = "./demo_dock.css"
    cats = dict()
    can_focus = True
    can_focus_children = True
    auto_expand=False
    highlighted_node = None
    selected_node = None
    init_select = False
    init_highlight = False
    class CategoryChanged(Message):
        def __init__(self, cat_path: str):
            super().__init__()
            self.cat_path = cat_path

    class CustomTestMessage(Message):
        def __init__(self):
            super().__init__()
    
    def on_mount(self):
        # Select the topmost node
        # self.select_node(self.root)
        self.highlighted_node = self.root
        self.selected_node = self.root
        # calendar_utils.add_highlight(self.selected_node)
        calendar_utils.add_left_arrow_tree(self.highlighted_node)
        # self.temp_node_selected()
        # self.select_node(self.selected_node)
        # self.action_select_cursor()

        self.line = 0
        self.cats = category_api.get_categories()
        self.root.expand()
        
        for cat in self.cats:
            top_cat = self.root.add(cat, expand=True, data={"color": self.cats[cat]['color']})
            top_cat.allow_expand = True
            calendar_utils.build_category_tree(top_cat, self.cats[cat]['subcategories'])
            
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
            icon = Text("● ", style=constants.CIRCLE_COLOR[node.data['color']])
        text = Text()
        text.append(icon)
        text.append(node_label)
        return text
        
    def on_tree_node_selected(self, event: Tree.NodeSelected):
        event.stop()
        # calendar_utils.remove_highlight(self.selected_node)
        # calendar_utils.add_highlight(event.node)
        full_cat_path = calendar_utils.get_full_path_from_node(event.node)
        self.selected_node = event.node
        self.post_message(self.CategoryChanged(full_cat_path))
        
        
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
    auto_expand=False
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
        
        resp = task_api.get_tags()
        if resp.status_code == 200:
            self.tags = general_utils.bytes2dict(resp.content)['tags']
        elif resp.status_code == 400:
            err_msg = general_utils.bytes2dict(resp.content)['detail']
            exit(0)
        else:
            exit(0)
        
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
        # calendar_utils.remove_highlight(self.selected_node)
        tag = str(event.node._label)
        if tag.endswith(" " + constants.LEFT_ARROW_EMOJI):
            tag = tag[:-2]

        self.post_message(self.TagChanged(tag))
        event.node.set_label(tag)
        # calendar_utils.add_highlight(event.node)
        self.selected_node = event.node
        # self.post_message(self.CustomTestMessage())
        
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

        

        
