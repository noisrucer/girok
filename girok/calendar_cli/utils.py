import calendar
from datetime import datetime

from rich.style import Style
from rich.text import Text
from textual import log
from textual.widgets.tree import TreeNode

from girok.constants import Emoji

 
def build_category_tree(tree_node: TreeNode, categories: list[dict]) -> None:
    for category in categories:
        if not category['children']:
            cur = tree_node.add_leaf(category['name'], data={"color": category['color'], 'id': category['id']})
        else:
            cur = tree_node.add(category['name'], expand=True, data={"color": category['color'], 'id': category['id']})
            build_category_tree(cur, category['children'])


def get_full_path_from_node(node):
    label = str(node._label)
    if label.endswith(" " + Emoji.LEFT_ARROW):
        label = label[:-2]
    else:
        pass
    if label == "All Categories":
        return ""
    elif label == "No Category":
        return "No Category"
    node_name = label
    parent_path = get_full_path_from_node(node.parent)
    return parent_path + node_name + "/"


def convert_day_to_cell_num(year: int, month: int, day: int):
    """ """
    first_weekday, total_days = calendar.monthrange(year, month)
    return first_weekday + day - 1


def convert_cell_num_to_day(year: int, month: int, cell_num: int):
    first_weekday, total_days = calendar.monthrange(year, month)
    return cell_num - first_weekday + 1


def convert_cell_num_to_coord(cell_num: int):
    """
    cell_num: 0 ~ 34
    """

    return (cell_num // 7, cell_num % 7)


def convert_coord_to_cell_num(x: int, y: int):
    return x * 7 + y


def get_date_obj_from_str_separated_by_T(s: str):
    s = str(s)
    delim = "T" if "T" in s else " "
    return datetime.strptime(s, f"%Y-%m-%d{delim}%H:%M:%S")


def remove_left_arrow(cell):
    if cell is None:
        return
    if not cell.children:
        return
    cell_label = cell.children[0]
    cell_label_text = cell_label.render()
    style = cell_label_text.style
    if str(cell_label_text).endswith(" " + Emoji.LEFT_ARROW):
        if cell_label_text.spans:
            style = cell_label_text.spans[0].style

    if str(cell_label_text).endswith(" " + Emoji.LEFT_ARROW):
        new_label_text = Text(str(cell_label_text)[:2])
    else:
        new_label_text = Text(str(cell_label_text))
    cell_label.update(new_label_text)


def add_left_arrow(cell):
    if not cell.children:
        return

    cell_label = cell.children[0]
    cell_label_text = cell_label.render()
    style = cell_label_text.style

    if str(cell_label_text).endswith(" " + Emoji.LEFT_ARROW):
        new_label_text = Text(str(cell_label_text), style=style)
    else:
        new_label_text = Text.assemble(
            Text(str(cell_label_text), style=style),
            " ",
            Text(Emoji.LEFT_ARROW, style=Style(color="#9bdfbb")),
        )
    cell_label.update(new_label_text)


def remove_left_arrow_tree(node):
    label_text = node.label
    style = label_text.style
    if str(label_text).endswith(" " + Emoji.LEFT_ARROW):
        new_label_text = Text(str(label_text)[:-2], style=style)
    else:
        new_label_text = Text(str(label_text), style=style)

    node.set_label(new_label_text)


def add_left_arrow_tree(node):
    label_text = node.label
    style = label_text.style
    if str(label_text).endswith(" " + Emoji.LEFT_ARROW):
        pass
    else:
        node.set_label(
            Text.assemble(label_text, " ", Emoji.LEFT_ARROW, style=style)
        )


def remove_highlight(node):
    label_text = node.label
    style = label_text.style
    node.set_label(Text(str(label_text)))


def add_highlight(node):
    label = str(node.label)
    node.set_label(Text(label, style=Style(color="#9bdfbb")))
