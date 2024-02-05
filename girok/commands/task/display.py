import calendar
from datetime import datetime
from typing import List, Literal, Optional

from rich import box, print
from rich.align import Align
from rich.tree import Tree
from rich.console import Console
from rich.style import Style
from rich.table import Column, Table
from rich.text import Text

from girok.commands.task.entity import Category, Event, EventDate, Repetition
from girok.commands.task.utils import cache_event_ids
from girok.constants import (
    TABLE_DATETIME_COLOR,
    TABLE_DEFAULT_TEXT_COLOR,
    TABLE_EVENT_DELETED_COLOR,
    TABLE_EVENT_HIGHLIGHT_COLOR,
    TABLE_EVENT_NAME_COLOR,
    TABLE_HEADER_TEXT_COLOR,
    Emoji,
    CATEGORY_COLOR_PALETTE,
    DEFAULT_CATEGORY_COLOR,
    EVENT_TREE_EVENT_COLOR,
    EVENT_TREE_CATEGORY_COLOR,
    EVENT_TREE_DATETIME_COLOR
)
from girok.utils.time import convert_iso_date_str_to_date_obj, get_day_offset


def display_events_by_list(
    events: List[Event],
    highlight_event_id: Optional[int] = None,
    highlight_action: Literal["highlight", "delete"] = None,
):
    """
    id
    name
    category path
    start datetime (8 December 2023, 7:30PM)
    end datetime (8 December 2023, 7:30PM)
    Tags
    Priority
    Memo
    Repetition
    Repetition End Date
    """
    num_events = len(events)
    table = Table(
        Column(
            header="ID",
            justify="center",
            header_style=Style(color=TABLE_HEADER_TEXT_COLOR),
            style=Style(color=TABLE_EVENT_NAME_COLOR),
        ),
        Column(
            header="Name", header_style=Style(color=TABLE_HEADER_TEXT_COLOR), style=Style(color=TABLE_EVENT_NAME_COLOR)
        ),
        Column(
            header="Category",
            justify="center",
            header_style=Style(color=TABLE_HEADER_TEXT_COLOR),
            style=Style(color=TABLE_DEFAULT_TEXT_COLOR),
        ),
        Column(
            header="Start date",
            justify="center",
            header_style=Style(color=TABLE_HEADER_TEXT_COLOR),
        ),
        Column(
            header="End date",
            justify="center",
            header_style=Style(color=TABLE_HEADER_TEXT_COLOR),
        ),
        Column(
            header="Repeat",
            justify="center",
            header_style=Style(color=TABLE_HEADER_TEXT_COLOR),
        ),
        Column(
            header="Tags",
            justify="center",
            header_style=Style(color=TABLE_HEADER_TEXT_COLOR),
        ),
        Column(
            header="Priority",
            justify="center",
            header_style=Style(color=TABLE_HEADER_TEXT_COLOR),
        ),
        Column(header="Memo", header_style=Style(color=TABLE_HEADER_TEXT_COLOR)),
        Column(header="Remaining", justify="center", header_style=Style(color=TABLE_HEADER_TEXT_COLOR)),
        box=box.SIMPLE_HEAVY,
        show_lines=False if num_events > 15 else True,
        border_style=Style(color="#D7E1C9", bold=True),
    )

    if highlight_event_id:
        highlight_color = TABLE_EVENT_HIGHLIGHT_COLOR if highlight_action == "highlight" else TABLE_EVENT_DELETED_COLOR
    else:
        highlight_color = None

    event_ids_cache = {}
    for idx, event in enumerate(events):
        # Cache event id
        event_ids_cache[idx + 1] = {"id": event.id, "name": event.name}

        # Build category path
        if event.category_path:
            category_str = "/".join([c.name for c in event.category_path])
        else:
            category_str = "-"

        # Build start time
        start_datetime_str = build_datetime_str(event.event_date.start_date, event.event_date.start_time)

        # Build end time
        end_datetime_str = build_datetime_str(event.event_date.end_date, event.event_date.end_time)

        # Build tags
        tag_str = ", ".join(event.tags) if event.tags else "-"

        # Build repetition
        repetition_type = event.repetition.repetition_type
        repetition_end_date = event.repetition.repetition_end_date
        if not repetition_type:
            repetition_str = "-"
        else:
            repetition_str = repetition_type
            if repetition_end_date:
                repetition_str += f" until {repetition_end_date}"

        # Remaining time
        remaining_days = get_day_offset(datetime.now(), convert_iso_date_str_to_date_obj(event.event_date.start_date))
        remaining_days_str = (
            f"{remaining_days} days left" if remaining_days > 0 else f"{abs(remaining_days)} days passed"
        )

        # Build priority
        priority_str = event.priority if event.priority else "-"

        # Build Memo
        if event.memo:
            memo_str = event.memo if len(event.memo) <= 30 else event.memo[:30] + "..."
        else:
            memo_str = "-"

        table.add_row(
            Text(str(idx + 1), style=Style(color=TABLE_DEFAULT_TEXT_COLOR)),  # id
            Text.assemble(  # name
                Text(Emoji.CIRCLE, style=Style(color=event.color_hex)),  # circle emoji
                " ",
                Text(
                    event.name,
                    style=Style(
                        color=highlight_color if highlight_event_id == event.id else TABLE_DEFAULT_TEXT_COLOR, bold=True
                    ),
                ),
            ),
            Text(  # category path
                category_str,
                style=Style(color=highlight_color if highlight_event_id == event.id else TABLE_DEFAULT_TEXT_COLOR),
            ),
            Text(  # start datetime
                start_datetime_str,
                style=Style(color=highlight_color if highlight_event_id == event.id else TABLE_DATETIME_COLOR),
            ),
            Text(  # end datetime
                end_datetime_str,
                style=Style(color=highlight_color if highlight_event_id == event.id else TABLE_DATETIME_COLOR),
            ),
            Text(
                repetition_str,
                style=Style(color=highlight_color if highlight_event_id == event.id else TABLE_DEFAULT_TEXT_COLOR),
            ),
            Text(  # Tags
                tag_str,
                style=Style(color=highlight_color if highlight_event_id == event.id else TABLE_DEFAULT_TEXT_COLOR),
            ),
            Text(  # priority
                priority_str,
                style=Style(color=highlight_color if highlight_event_id == event.id else TABLE_DEFAULT_TEXT_COLOR),
            ),
            Text(
                memo_str,
                style=Style(color=highlight_color if highlight_event_id == event.id else TABLE_DEFAULT_TEXT_COLOR),
            ),
            Text(
                remaining_days_str,
                style=Style(color=highlight_color if highlight_event_id == event.id else TABLE_DEFAULT_TEXT_COLOR),
            ),
        )

    cache_event_ids(event_ids_cache)
    print(Align(table, align="center"))
    return table


def display_events_by_tree(
    categories: List[dict],
    events: List[Event],
    highlight_event_id: Optional[int] = None,
    highlight_action: Literal["highlight", "delete"] = None,
):
    event_ids_cache = {}
    category_tree = {
        "No Category": {
            "subcategories": {},
            "events": [],
            "color": DEFAULT_CATEGORY_COLOR
        },
    }

    # Build category tree
    for category in categories:
        build_category_tree(category_tree, category)

    for event in events:
        category_path = event.category_path
        if not category_path:
            category_tree['No Category']['events'].append(event)
        else:
            recursively_create_category_path(category_tree, category_path, event)
    
    tree_obj = Tree("")
    for category_name, category_tree_dict in category_tree.items():
        subtree_obj = get_event_subtree(
            category_tree=category_tree_dict,
            current_category_name=category_name,
            event_ids_cache=event_ids_cache,
            highlight_event_id=highlight_event_id,
            highlight_action=highlight_action
        )
        tree_obj.add(subtree_obj)
    
    # Cache ids
    cache_event_ids(event_ids_cache)
    print(tree_obj)


def build_category_tree(category_tree: dict, category: dict):
    category_tree[category['name']] = {
        "subcategories": {},
        "events": [],
        "color": CATEGORY_COLOR_PALETTE[category['color']]
    }

    for child in category['children']:
        build_category_tree(category_tree[category['name']]['subcategories'], child)



def get_event_subtree(
    category_tree: dict,
    current_category_name: str,
    event_ids_cache: dict,
    highlight_event_id: Optional[int] = None,
    highlight_action: Literal["highlight", "delete"] = None,
):
    current_node_text = Text.assemble(
        Text(
            Emoji.CIRCLE,
            style=Style(color=category_tree['color'])
        ),
        " ",
        Text(
            f"{current_category_name}",
            style=Style(color=TABLE_HEADER_TEXT_COLOR)
        )
    )
    tree_obj = Tree(current_node_text)
    
    for child_category_name in category_tree['subcategories']:
        sub_tree_obj = get_event_subtree(
            category_tree=category_tree['subcategories'][child_category_name],
            current_category_name=child_category_name,
            event_ids_cache=event_ids_cache,
            highlight_event_id=highlight_event_id,
            highlight_action=highlight_action
        )
        tree_obj.add(sub_tree_obj)

    for event in category_tree['events']:
        event: Event = event

        # Cache event id
        if not (event.id == highlight_event_id and highlight_action == 'delete'):
            event_ids_cache[len(event_ids_cache) + 1] = {"id": event.id, "name": event.name}
        
        event_id = len(event_ids_cache)

        # Remaining time
        remaining_days = get_day_offset(datetime.now(), convert_iso_date_str_to_date_obj(event.event_date.start_date))
        remaining_days_str = (
            f"{remaining_days} days left" if remaining_days > 0 else f"{abs(remaining_days)} days passed"
        )

        # Start time
        start_datetime_str = build_datetime_str(event.event_date.start_date, event.event_date.start_time)
        weekday_str = calendar.day_abbr[convert_iso_date_str_to_date_obj(event.event_date.start_date).weekday()]
        start_datetime_str += f", {weekday_str}"

        # Build event tree
        node_text = Text.assemble(
            Text(
                f"[{event_id}]"
            ),
            " ",
            Text(
                event.name,
                style=Style(color=EVENT_TREE_EVENT_COLOR, bold=True)
            ),
            " ",
            Text(
                f"[{remaining_days_str}]",
            ),
            " - ",
            Text(
                start_datetime_str,
                style=Style(color=EVENT_TREE_DATETIME_COLOR)
            ),
            style=Style(
                strike=True if event.id == highlight_event_id and highlight_action == 'delete' else False
            )
        )
        tree_obj.add(node_text)
    
    return tree_obj


        
def recursively_create_category_path(tree: dict, category_path: List[Category], event: Event) -> None:
    # A, B
    if len(category_path) == 0:
        raise ValueError("Category path must be equal or greater than 1")

    cur_category = category_path[0]
    if cur_category.name not in tree:
        tree[cur_category.name] = {
            "subcategories": {},
            "events": []
        }
    
    if len(category_path) == 1:
        tree[cur_category.name]['events'].append(event)
    else:
        recursively_create_category_path(tree[cur_category.name]['subcategories'], category_path[1:], event)


def build_datetime_str(date_str: Optional[str], time_str: Optional[str]) -> str:
    # Process date
    if not date_str:
        return "-"

    date_obj = convert_iso_date_str_to_date_obj(date_str)
    year = date_obj.year
    month = date_obj.month
    day = date_obj.day
    formatted_date_str = f"{day} {calendar.month_abbr[month]} {year}"

    # Process time
    if not time_str:
        return formatted_date_str

    h, m, s = time_str.split(":")
    h = int(h)
    afternoon = h >= 12
    if h > 12:
        h -= 12
    formatted_time_str = f"{h}:{m}{'PM' if afternoon else 'AM'}"
    return formatted_date_str + ", " + formatted_time_str
