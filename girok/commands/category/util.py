from typing import Optional

from rich import print
from rich.console import Console
from rich.style import Style
from rich.text import Text
from rich.tree import Tree

from girok.constants import (
    CATEGORY_COLOR_PALETTE,
    DEFAULT_CATEGORY_TEXT_COLOR,
    HIGHLIGHT_CATEGORY_TEXT_COLOR,
    DisplayBoxType,
    Emoji,
)
from girok.constants import CONFIG_PATH, CATEGORY_COLOR_AUTO_ASSIGNMENT_ORDER
from girok.utils.json_utils import read_json, update_json

console = Console()


def display_categories_tree(root_categories: list[dict], highlight_category_path: Optional[str] = None):
    """Display the category tree

    Args:
        root_categories (list[dict]): List of top-level categories.
        highlight_category_path (Optional[str], optional): Category path name to be highlighted. Must be in 'A/B/C' format. Defaults to None.
    """
    tree = Tree("")

    for category in root_categories:
        display_category_subtree(
            tree=tree,
            category=category,
            highlight_category_path=highlight_category_path,
        )
    console.print(tree)


def display_category_subtree(
    tree: Tree,
    category: dict,
    highlight_category_path: Optional[str] = None,
    parent_cumul_path: str = "",
):
    """Display the subtree of a single tree node.

    Args:
        tree (Tree): rich.tree.Tree object.
        category (dict): A single category. It's a dictionary with keys 'id', 'name', 'color', 'children'
        highlight_category_path (Optional[str], optional): Category path name to be highlighted. Must be in 'A/B/C' format. Defaults to None.
        parent_cumul_path (str, optional): The cumulative category path string of the current node's parent. Defaults to "".
    """
    category_name = category["name"]
    category_color = category["color"]
    category_children = category["children"]
    current_category_path = f"{parent_cumul_path}/{category_name}".lstrip("/")  # A/B/C

    circle_text = Text(text=Emoji.CIRCLE, style=Style(color=CATEGORY_COLOR_PALETTE[category_color]))

    category_name_text = Text(
        text=f"{category_name}",
        style=Style(
            color=(
                DEFAULT_CATEGORY_TEXT_COLOR
                if highlight_category_path != current_category_path
                else HIGHLIGHT_CATEGORY_TEXT_COLOR
            )
        ),
    )

    item_text = Text.assemble(circle_text, " ", category_name_text)
    sub_tree = tree.add(item_text)
    for child in category_children:
        display_category_subtree(
            tree=sub_tree,
            category=child,
            highlight_category_path=highlight_category_path,
            parent_cumul_path=current_category_path,
        )


def get_next_category_color() -> str:
    cfg = read_json(CONFIG_PATH)

    if "next_category_color_idx" in cfg:
        next_category_color_idx = cfg["next_category_color_idx"]
    else:
        next_category_color_idx = 0
    
    next_category_color = CATEGORY_COLOR_AUTO_ASSIGNMENT_ORDER[next_category_color_idx]
    next_category_color_idx = (next_category_color_idx + 1) % len(CATEGORY_COLOR_AUTO_ASSIGNMENT_ORDER)
    update_json(CONFIG_PATH, {"next_category_color_idx": next_category_color_idx})
    return next_category_color