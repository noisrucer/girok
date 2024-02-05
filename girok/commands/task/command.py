import calendar
from datetime import datetime, timedelta
from typing import List, Optional

import typer
from rich import print
from typing_extensions import Annotated

import girok.api.category as category_api
import girok.api.task as task_api
from girok.commands.task.callbacks import (
    allow_empty_category_callback,
    date_callback,
    datetime_callback,
    not_allow_empty_category_callback,
    priority_callback,
    tags_callback,
    valid_integer_callback,
)
from girok.commands.task.display import display_events_by_list, display_events_by_tree
from girok.commands.task.entity import Category, Event, EventDate, Repetition
from girok.commands.task.utils import decode_date_format, validate_start_end_window
from girok.constants import EVENT_IDS_CACHE_PATH, REPETITION_TYPE, DisplayBoxType
from girok.utils.display import center_print
from girok.utils.json_utils import read_json
from girok.utils.time import build_date_info, convert_date_obj_to_iso_date_str

app = typer.Typer(rich_markup_mode="rich")


@app.command(
    "addtask",
    help="[yellow]Add[/yellow] a new task",
    rich_help_panel=":fire: [bold yellow1]Task Commands[/bold yellow1]",
)
def add_task(
    name: Annotated[str, typer.Argument(help="Task name")],
    start_datetime: Annotated[
        str, typer.Option("-d", "--date", help="[yellow]Task start datetime[/yellow]", callback=datetime_callback)
    ],
    end_datetime: Annotated[
        Optional[str],
        typer.Option("-e", "--end", help="[yellow]Task end datetime[/yellow]", callback=datetime_callback),
    ] = None,
    repetition: Annotated[
        Optional[str],
        typer.Option(
            "-r",
            "--repetition",
            help="[yellow]Task repetition type. One of 'daily', 'weekly', 'monthly', 'yearly'[/yellow]",
        ),
    ] = None,
    category_path: Annotated[
        Optional[str],
        typer.Option(
            "-c",
            "--category",
            help="[yellow]Category path - xx/yy/zz..[/yellow]",
            callback=allow_empty_category_callback,
        ),
    ] = None,
    tags: Annotated[
        Optional[str],
        typer.Option(
            "-t",
            "--tag",
            help="[yellow]Tags[/yellow]. Multiple tags must be provided in 'A,B,C' format.",
            callback=tags_callback,
        ),
    ] = None,
    priority: Annotated[
        Optional[str], typer.Option("-p", "--priority", help="[yellow]Priority[/yellow]", callback=priority_callback)
    ] = None,
    memo: Annotated[Optional[str], typer.Option("-m", "--memo", help="[yellow]Memo[/yellow]")] = None,
):
    """
    Validate time combination. The possible combinations are:
    1. start_date
    2. start_date, start_time
    3. start_date, end_date
    4. start_date, start_time, end_date, end_time
    """
    start_date, start_time = start_datetime
    end_date, end_time = None, None
    if end_datetime:
        end_date, end_time = end_datetime

    valid, err_msg = validate_start_end_window(start_date, start_time, end_date, end_time)
    if not valid:
        raise typer.BadParameter(err_msg)

    # Convert tags to list
    if tags:
        tags = tags.split(",")

    # Validate repetition
    repetition_type = None
    repetition_end_date = None
    if repetition:
        # Repetition is only allowed for single-day event
        if (start_date and end_date) and (start_date != end_date):
            raise typer.BadParameter("Repetition is only allowed for single-day event")

        if "@" not in repetition:  # daily
            if repetition not in REPETITION_TYPE:
                raise typer.BadParameter("Repetition type must be one of 'daily', 'weekly', 'monthly', 'yearly'")
            repetition_type = repetition
        else:  # daily@5/14
            repetition_items = repetition.split("@")
            if len(repetition_items) != 2:
                raise typer.BadParameter("Invalid repetition input format")

            repetition_type, repetition_end_date_str = repetition_items
            if repetition_type not in REPETITION_TYPE:
                raise typer.BadParameter("Repetition type must be one of 'daily', 'weekly', 'monthly', 'yearly'")

            valid, iso_date_str = decode_date_format(repetition_end_date_str)
            if not valid:
                raise typer.BadParameter("Invalid repetition end date format")

            repetition_end_date = iso_date_str

            # Repetition end date must be greater than start_date
            repetition_end_date_obj = datetime.strptime(repetition_end_date, "%Y-%m-%d").date()
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            if repetition_end_date_obj <= start_date_obj:
                raise typer.BadParameter("Repetition end date must be greater than start date")

        repetition_type = REPETITION_TYPE[repetition_type]

    resp = task_api.create_task(
        name=name,
        start_date=start_date,
        start_time=start_time,
        end_date=end_date,
        end_time=end_time,
        repetition_type=repetition_type,
        repetition_end_date=repetition_end_date,
        category_path=category_path,
        tags=tags,
        priority=priority,
        memo=memo,
    )
    if not resp.is_success:
        center_print(resp.error_message, DisplayBoxType.ERROR)
        raise typer.Exit()

    # Display Tasks
    created_event_id = resp.body["eventId"]
    resp = task_api.get_all_tasks()
    if not resp.is_success:
        center_print(resp.error_message, DisplayBoxType.ERROR)
        raise typer.Exit()

    events = resp.body["events"]
    event_entities = map_to_event_entities(events)
    display_events_by_list(event_entities, highlight_event_id=created_event_id, highlight_action="highlight")


@app.command(
    "showtask",
    help="[yellow]View[/yellow] tasks with options",
    rich_help_panel=":fire: [bold yellow1]Task Commands[/bold yellow1]",
)
def showtask(
    category_path: Annotated[
        Optional[str],
        typer.Option(
            "-c",
            "--category",
            help="[yellow]Category path - xx/yy/zz..[/yellow]",
            callback=not_allow_empty_category_callback,
        ),
    ] = None,
    tags: Annotated[
        Optional[str],
        typer.Option(
            "-t",
            "--tag",
            help="[yellow]Tags[/yellow]. Multiple tags must be provided in 'A,B,C' format.",
            callback=tags_callback,
        ),
    ] = None,
    priority: Annotated[
        Optional[str], typer.Option("-p", "--priority", help="[yellow]Priority[/yellow]", callback=priority_callback)
    ] = None,
    exact_date: Annotated[
        Optional[str], typer.Option("-e", "--exact", help="[yellow]Exact Deadline[/yellow]", callback=date_callback)
    ] = None,
    within_days: Annotated[
        Optional[int],
        typer.Option(
            "-d",
            "--day",
            help="Show tasks due [yellow]within the specified days[/yellow]",
            callback=valid_integer_callback,
        ),
    ] = None,
    within_weeks: Annotated[
        Optional[int],
        typer.Option(
            "-w",
            "--week",
            help="Show tasks due [yellow]within the specified weeks[/yellow]",
            callback=valid_integer_callback,
        ),
    ] = None,
    within_months: Annotated[
        Optional[int],
        typer.Option(
            "-m",
            "--month",
            help="Show tasks due [yellow]within the specified months[/yellow]",
            callback=valid_integer_callback,
        ),
    ] = None,
    within_this_week: Annotated[
        Optional[bool],
        typer.Option(
            "-tw",
            "--this-week",
            help="Show tasks due [yellow]within this week[/yellow]",
        ),
    ] = None,
    within_next_week: Annotated[
        Optional[bool],
        typer.Option(
            "-nw",
            "--next-week",
            help="Show tasks due [yellow]within next week[/yellow]",
        ),
    ] = None,
    within_this_month: Annotated[
        Optional[bool],
        typer.Option(
            "-tm",
            "--this-month",
            help="Show tasks due [yellow]within this month[/yellow]",
        ),
    ] = None,
    within_next_month: Annotated[
        Optional[bool],
        typer.Option(
            "-nm",
            "--next-month",
            help="Show tasks due [yellow]within next month[/yellow]",
        ),
    ] = None,
    today: Annotated[
        Optional[bool],
        typer.Option(
            "-tdy",
            "--today",
            help="Show tasks due [yellow]today[/yellow]",
        ),
    ] = None,
    tomorrow: Annotated[
        Optional[bool],
        typer.Option(
            "-tmr",
            "--tomorrow",
            help="Show tasks due [yellow]tomorrow[/yellow]",
        ),
    ] = None,
    urgent: Annotated[
        Optional[bool], typer.Option("-u", "--urgent", help="Show [yellow]urgent[/yellow] tasks (due within 3 days)")
    ] = None,
    tree_view: Annotated[
        Optional[bool],
        typer.Option(
            '--tree',
            help="[yellow]Show tasks in a tree view[/yellow]"
        )
    ] = None
):
    # Resolve start_date and end_date
    """
    1. exact_date -> [start, end]
    2. within_days -> [-inf, end]
    3. within_weeks -> [-inf, end]
    4. within_months -> [-inf, month]
    5. within_this_week -> [-inf, end]
    6. within_next_week -> [-inf, end]
    7. within_this_month -> [-inf, end]
    8. within_next_month -> [-inf, end]
    9. today -> [start, end]
    10. tomorrow -> [start, end]
    11. urgent -> [today, end]
    -> else -> [-inf, inf]
    """
    date_options_cnt = sum(
        [
            opt is not None
            for opt in [
                exact_date,
                within_days,
                within_weeks,
                within_months,
                today,
                tomorrow,
                within_this_week,
                within_next_week,
                within_this_month,
                within_next_month,
            ]
        ]
    )
    if date_options_cnt > 1:
        raise typer.BadParameter("You can specify only one date option.")

    start_date, end_date = "2000-01-01", convert_date_obj_to_iso_date_str(datetime.now() + timedelta(days=365))
    if exact_date:
        start_date, end_date = exact_date, exact_date
    if within_days:
        end_date = convert_date_obj_to_iso_date_str(datetime.now() + timedelta(days=within_days - 1))
    if within_weeks:
        end_date = convert_date_obj_to_iso_date_str(datetime.now() + timedelta(days=7 * within_weeks))
    if within_months:
        end_date = convert_date_obj_to_iso_date_str(datetime.now() + timedelta(days=30 * within_months))
    if within_this_week:
        delta = 6 - datetime.today().weekday()
        end_date = convert_date_obj_to_iso_date_str(datetime.today() + timedelta(days=delta))
    if within_next_week:
        next_week = datetime.today() + timedelta(days=7)
        delta = 6 - next_week.weekday()
        end_date = convert_date_obj_to_iso_date_str(next_week + timedelta(days=delta))
    if within_this_month:
        today_date = datetime.today()
        _, last_day = calendar.monthrange(today_date.year, today_date.month)
        end_date = convert_date_obj_to_iso_date_str(datetime(today_date.year, today_date.month, last_day))
    if within_next_month:
        today_date = datetime.today()
        if today_date.month == 12:
            first_day_next_month = datetime(today_date.year + 1, 1, 1)
        else:
            first_day_next_month = datetime(today_date.year, today_date.month + 1, 1)
        _, last_day = calendar.monthrange(first_day_next_month.year, first_day_next_month.month)
        end_date = convert_date_obj_to_iso_date_str(
            datetime(first_day_next_month.year, first_day_next_month.month, last_day)
        )
    if today:
        start_date, end_date = convert_date_obj_to_iso_date_str(datetime.now()), convert_date_obj_to_iso_date_str(
            datetime.now()
        )
    if tomorrow:
        start_date, end_date = convert_date_obj_to_iso_date_str(
            datetime.now() + timedelta(1)
        ), convert_date_obj_to_iso_date_str(datetime.now() + timedelta(1))
    if urgent:
        start_date, end_date = convert_date_obj_to_iso_date_str(datetime.now()), convert_date_obj_to_iso_date_str(
            datetime.now() + timedelta(days=2)
        )

    # Resolve category id
    category_id = None
    if category_path:
        resp = category_api.get_category_id_by_path(category_path.split("/"))
        if not resp.is_success:
            center_print(resp.error_message, DisplayBoxType.ERROR)
            raise typer.Exit()
        category_id = resp.body["categoryId"]

    if tags:
        tags = tags.split("/")

    resp = task_api.get_all_tasks(
        start_date=start_date, end_date=end_date, category_id=category_id, priority=priority, tags=tags
    )
    if not resp.is_success:
        center_print(resp.error_message, DisplayBoxType.ERROR)
        raise typer.Exit()

    events = resp.body["events"]

    # Display Events
    event_entities = map_to_event_entities(events)
    center_print(build_date_info(datetime.now()), DisplayBoxType.TITLE)
    if tree_view:
        resp = category_api.get_all_categories()
        if not resp.is_success:
            center_print("Unable to fetch categories", DisplayBoxType.ERROR)
            raise typer.Exit()
        categories = resp.body['rootCategories']
        display_events_by_tree(categories, event_entities)
    else:
        display_events_by_list(event_entities)


@app.command(
    "done",
    help="[red]Delete[/red] a task",
    rich_help_panel=":fire: [bold yellow1]Task Commands[/bold yellow1]",
)
def remove_event(
    event_id: Annotated[int, typer.Argument(help="[yellow]Task ID[/yellow] to be deleted")],
    force: Annotated[Optional[bool], typer.Option("-y", "--yes", help="Don't show the confirmation message")] = False,
):
    try:
        cache = read_json(EVENT_IDS_CACHE_PATH)
    except:
        center_print("First type 'showtask' command to retrieve task ids", DisplayBoxType.ERROR)
        raise typer.Exit()

    if str(event_id) not in cache:
        center_print(f"Task id {event_id} is not found. Please enter 'showtask' command to view task ids.", DisplayBoxType.ERROR)
        raise typer.Exit()
    cached_event = cache[str(event_id)]

    target_event_id = cached_event["id"]
    target_event_name = cached_event["name"]

    if not force:
        done_confirm = typer.confirm(f"Are you sure to delete task [{target_event_name}]?")
        if not done_confirm:
            raise typer.Exit()

    # Display events
    resp = task_api.get_all_tasks()
    if not resp.is_success:
        center_print(resp.error_message, DisplayBoxType.ERROR)
        raise typer.Exit()

    events = resp.body["events"]
    event_entities = map_to_event_entities(events)

    # Remove events
    resp = task_api.remove_event(target_event_id)
    if not resp.is_success:
        center_print(resp.error_message, DisplayBoxType.ERROR)
        raise typer.Exit()

    center_print("Task was successfully deleted!", DisplayBoxType.SUCCESS)
    display_events_by_list(event_entities, highlight_event_id=target_event_id, highlight_action="delete")


def map_to_event_entities(events: List[dict]) -> List[Event]:
    event_entities: List[Event] = []
    for event in events:
        event_entity = Event(
            id=event["id"],
            name=event["name"],
            color_str=event["color"],
            tags=event["tags"],
            priority=event["priority"],
            memo=event["memo"],
            event_date=EventDate(
                start_date=event["eventDate"]["startDate"],
                start_time=event["eventDate"]["startTime"],
                end_date=event["eventDate"]["endDate"],
                end_time=event["eventDate"]["endTime"],
            ),
            repetition=Repetition(
                repetition_type=event["repetition"]["repetitionType"],
                repetition_end_date=event["repetition"]["repetitionEndDate"],
            ),
            category_path=[Category(id=c["categoryId"], name=c["categoryName"]) for c in event["categoryPath"]],
        )

        event_entities.append(event_entity)

    def sort_key(event: Event):
        # Handle None values for start_time and end_time by replacing them with "00:00"
        start_time = event.event_date.start_time if event.event_date.start_time else "00:00"
        end_time = event.event_date.end_time if event.event_date.end_time else "00:00"
        # Handle None for end_date by using start_date
        end_date = event.event_date.end_date if event.event_date.end_date else event.event_date.start_date

        return (event.event_date.start_date, start_time, end_date, end_time)

    event_entities.sort(key=sort_key)
    return event_entities


@app.command(
    "uptask",
    help="[yellow]Update[/yellow] a new task",
    rich_help_panel=":fire: [bold yellow1]Task Commands[/bold yellow1]",
)
def update_task(
    event_id: Annotated[
        int,
        typer.Argument(
            help="[yellow]Task ID[/yellow]"
        )
    ],
    name: Annotated[
        Optional[str],
        typer.Option(
            '-n', '--name',
            help="Task name"
        )
    ] = None,
    start_datetime: Annotated[
        Optional[str],
        typer.Option("-d", "--date", help="[yellow]Task start datetime[/yellow]", callback=datetime_callback)
    ] = None,
    end_datetime: Annotated[
        Optional[str],
        typer.Option("-e", "--end", help="[yellow]Task end datetime[/yellow]", callback=datetime_callback),
    ] = None,
    repetition: Annotated[
        Optional[str],
        typer.Option(
            "-r",
            "--repetition",
            help="[yellow]Task repetition type. One of 'daily', 'weekly', 'monthly', 'yearly'[/yellow]",
        ),
    ] = None,
    category_path: Annotated[
        Optional[str],
        typer.Option(
            "-c",
            "--category",
            help="[yellow]Category path - xx/yy/zz..[/yellow]",
            callback=allow_empty_category_callback,
        ),
    ] = None,
    tags: Annotated[
        Optional[str],
        typer.Option(
            "-t",
            "--tag",
            help="[yellow]Tags[/yellow]. Multiple tags must be provided in 'A,B,C' format.",
            callback=tags_callback,
        ),
    ] = None,
    priority: Annotated[
        Optional[str], typer.Option("-p", "--priority", help="[yellow]Priority[/yellow]", callback=priority_callback)
    ] = None,
    memo: Annotated[Optional[str], typer.Option("-m", "--memo", help="[yellow]Memo[/yellow]")] = None,
):
    try:
        cache = read_json(EVENT_IDS_CACHE_PATH)
    except:
        center_print("First type 'showtask' command to retrieve task ids", DisplayBoxType.ERROR)
        raise typer.Exit()

    if str(event_id) not in cache:
        center_print(f"Task id {event_id} is not found. Please enter 'showtask' command to view task ids.", DisplayBoxType.ERROR)
        raise typer.Exit()
    cached_event = cache[str(event_id)]

    target_event_id = cached_event["id"]

    """
    Validate time combination. The possible combinations are:
    1. start_date
    2. start_date, start_time
    3. start_date, end_date
    4. start_date, start_time, end_date, end_time
    """
    start_date, start_time = None, None
    if start_datetime:
        start_date, start_time = start_datetime

    end_date, end_time = None, None
    if end_datetime:
        end_date, end_time = end_datetime
    
    if start_date or start_time or end_date or end_time:
        valid, err_msg = validate_start_end_window(start_date, start_time, end_date, end_time)
        if not valid:
            raise typer.BadParameter(err_msg)

    # Convert tags to list
    if tags:
        tags = tags.split(",")

    # Validate repetition
    repetition_type = None
    repetition_end_date = None
    if repetition:
        # Repetition is only allowed for single-day event
        if (start_date and end_date) and (start_date != end_date):
            raise typer.BadParameter("Repetition is only allowed for single-day event")

        if "@" not in repetition:  # daily
            if repetition not in REPETITION_TYPE:
                raise typer.BadParameter("Repetition type must be one of 'daily', 'weekly', 'monthly', 'yearly'")
            repetition_type = repetition
        else:  # daily@5/14
            repetition_items = repetition.split("@")
            if len(repetition_items) != 2:
                raise typer.BadParameter("Invalid repetition input format")

            repetition_type, repetition_end_date_str = repetition_items
            if repetition_type not in REPETITION_TYPE:
                raise typer.BadParameter("Repetition type must be one of 'daily', 'weekly', 'monthly', 'yearly'")

            valid, iso_date_str = decode_date_format(repetition_end_date_str)
            if not valid:
                raise typer.BadParameter("Invalid repetition end date format")

            repetition_end_date = iso_date_str

            # Repetition end date must be greater than start_date
            repetition_end_date_obj = datetime.strptime(repetition_end_date, "%Y-%m-%d").date()
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            if repetition_end_date_obj <= start_date_obj:
                raise typer.BadParameter("Repetition end date must be greater than start date")

        repetition_type = REPETITION_TYPE[repetition_type]

    
    # Get the target event
    resp = task_api.get_single_event(target_event_id)
    if not resp.is_success:
        center_print(resp.error_message, DisplayBoxType.ERROR)
        raise typer.Exit()
    event = resp.body

    if category_path is None:
        category_path = '/'.join([c['categoryName'] for c in event['categoryPath']])    

    resp = task_api.update_task(
        event_id=target_event_id,
        name=name if name else event['name'],
        start_date=start_date if start_date else event['eventDate']['startDate'],
        start_time=start_time if start_time else event['eventDate']['startTime'],
        end_date=end_date if end_date else event['eventDate']['endDate'],
        end_time=end_time if end_time else event['eventDate']['endTime'],
        repetition_type=repetition_type if repetition_type else event['repetition']['repetitionType'],
        repetition_end_date=repetition_end_date if repetition_end_date else event['repetition']['repetitionEndDate'],
        category_path=category_path,
        tags=tags if tags else event['tags'],
        priority=priority if priority else event['priority'],
        memo=memo if memo else event['memo'],
    )
    if not resp.is_success:
        center_print(resp.error_message, DisplayBoxType.ERROR)
        raise typer.Exit()

    # Display Tasks
    resp = task_api.get_all_tasks()
    if not resp.is_success:
        center_print(resp.error_message, DisplayBoxType.ERROR)
        raise typer.Exit()

    events = resp.body["events"]
    event_entities = map_to_event_entities(events)
    display_events_by_list(event_entities, highlight_event_id=target_event_id, highlight_action="highlight")
